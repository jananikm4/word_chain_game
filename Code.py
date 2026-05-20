import streamlit as st
import random
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Word Chain Game", page_icon="🧠", layout="centered")

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def is_valid_word(word: str) -> bool:
    """Validate against Free Dictionary API. Cached so same word isn't re-checked."""
    try:
        r = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=3,
        )
        return r.status_code == 200
    except requests.RequestException:
        # Network hiccup — be lenient rather than punishing the player
        return True


def bot_pick(letter: str, used_list: list) -> str | None:
    """
    Ask the dictionary API for real words starting with `letter`.
    Falls back to a curated seed list if the API doesn't cooperate.
    """
    SEEDS = [
        "apple", "elephant", "tiger", "rabbit", "rose", "snake",
        "engine", "echo", "orange", "anchor", "eagle", "igloo",
        "noodle", "exit", "tongue", "envelope", "umbrella",
        "antelope", "octopus", "sunrise", "evening", "globe",
        "blanket", "tree", "egg", "garden", "night", "honey", 
        "yarn", "nail", "lake", "kettle",
    ]

    # Convert to set internally for O(1) lookups during selection
    used_set = set(used_list)

    # First try seeds (fast, offline)
    candidates = [w for w in SEEDS if w.startswith(letter) and w not in used_set]
    if candidates:
        return random.choice(candidates)

    # Try the API to find a real word starting with `letter` via simple prefixes
    attempts = [letter + suffix for suffix in ["at", "an", "en", "in", "on", "est", "ight", "ound"]]
    for attempt in attempts:
        if attempt not in used_set and is_valid_word(attempt):
            return attempt

    return None  # Bot is genuinely stuck — player wins!


def reset_game():
    seed_words = ["apple", "orange", "tiger", "engine", "rabbit", "eagle"]
    start = random.choice(seed_words)
    st.session_state.current_word = start
    st.session_state.score = 0
    st.session_state.used = [start]  # Maintained as a list to preserve chronological order
    st.session_state.message = ("info", f"Game started! First word is **{start.upper()}**.")
    st.session_state.game_over = False
    st.session_state.input_key = st.session_state.get("input_key", 0) + 1


# ── State init ────────────────────────────────────────────────────────────────
if "high_score" not in st.session_state:
    st.session_state.high_score = 0

if "current_word" not in st.session_state:
    st.session_state.input_key = 0
    reset_game()

# Update high score persistently
if st.session_state.score > st.session_state.high_score:
    st.session_state.high_score = st.session_state.score


# ── UI Layout ─────────────────────────────────────────────────────────────────
st.title("🧠 Word Chain Game")

# Updated caption to explain the scoring system clearly
st.caption("Chain real English words — each word must start with the last letter of the previous one. ")
st.caption("💡 **Scoring:** You earn 1 point per letter (longer words give more points!).")

# Game stats panel
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current word", st.session_state.current_word.upper())
col2.metric("Your score", st.session_state.score)
col3.metric("🏆 High Score", st.session_state.high_score)
col4.metric("Words used", len(st.session_state.used))

st.divider()

# Message banner processing
msg_type, msg_text = st.session_state.get("message", ("info", ""))
if msg_text:
    if msg_type == "success":
        st.success(msg_text)
    elif msg_type == "error":
        st.error(msg_text)
    elif msg_type == "warning":
        st.warning(msg_text)
    else:
        st.info(msg_text)

# Main Game Interaction Loop
if not st.session_state.game_over:
    required_letter = st.session_state.current_word[-1].upper()
    st.markdown(f"Next word must start with: **{required_letter}**")

    # Native submission on enter press is optimized via form structure
    with st.form(key=f"game_form_{st.session_state.input_key}", clear_on_submit=True):
        user_word = st.text_input(
            "Your word",
            placeholder=f"Type a word starting with '{required_letter}'…",
            label_visibility="collapsed"
        ).strip().lower()
        
        col_sub, col_reset = st.columns([1, 1])
        submitted = col_sub.form_submit_button("Submit Word ✅", use_container_width=True)
        reset_pressed = col_reset.form_submit_button("New Game 🔄", use_container_width=True)

    if reset_pressed:
        reset_game()
        st.rerun()

    if submitted:
        # ── Game Validation Logic ─────────────────────────────────────────────
        if not user_word:
            st.session_state.message = ("warning", "Please enter a word first!")
            st.rerun()

        elif user_word in st.session_state.used:
            st.session_state.message = ("error", f"**{user_word.upper()}** has already been used. Try another!")
            st.rerun()

        elif not user_word.startswith(required_letter.lower()):
            st.session_state.message = (
                "error",
                f"**{user_word.upper()}** doesn't start with **{required_letter}**. Try again!",
            )
            st.rerun()

        elif not is_valid_word(user_word):
            st.session_state.message = ("error", f"**{user_word.upper()}** isn't a recognized English word.")
            st.rerun()

        else:
            # ── Valid player move ─────────────────────────────────────────────
            # Dynamic Scoring: Reward longer words!
            gained_points = len(user_word)
            st.session_state.score += gained_points
            st.session_state.used.append(user_word)
            st.session_state.current_word = user_word
            st.session_state.input_key += 1 

            # Bot's counter-turn
            bot_letter = user_word[-1]
            bot_word = bot_pick(bot_letter, st.session_state.used)

            if bot_word is None:
                # Player victory path
                st.session_state.message = (
                    "success",
                    f"🎉 You win! I couldn't find an available word starting with "
                    f"**{bot_letter.upper()}**. Your final score: **{st.session_state.score}**",
                )
                st.session_state.game_over = True
            else:
                st.session_state.used.append(bot_word)
                st.session_state.current_word = bot_word
                st.session_state.message = (
                    "info",
                    f"Nice word (+{gained_points} pts)! My counter word is **{bot_word.upper()}** — "
                    f"now you need a word starting with **{bot_word[-1].upper()}**",
                )
            st.rerun()

else:
    # Post-game screen
    st.write("---")
    if st.button("Play again 🔄", use_container_width=True):
        reset_game()
        st.rerun()

# ── Chronological Word Chain History ──────────────────────────────────────────
st.write("")
with st.expander("📜 Word Chain History", expanded=True):
    if st.session_state.used:
        st.write(" ➡️ ".join([f"**{w.upper()}**" for w in st.session_state.used]))
    else:
        st.info("No words logged yet.")
