import streamlit as st
import random
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Word Chain Game", page_icon="🧠")

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def is_valid_word(word: str) -> bool:
    """Validate against Free Dictionary API. Cached so same word isn't re-checked."""
    try:
        r = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=5,
        )
        return r.status_code == 200
    except requests.RequestException:
        # Network hiccup — be lenient rather than punishing the player
        return True


def bot_pick(letter: str, used: set) -> str | None:
    """
    Ask the dictionary API for real words starting with `letter`.
    Falls back to a curated seed list if the API doesn't cooperate.
    """
    # Seed list — only used as fallback; game isn't limited to these
    SEEDS = [
        "apple", "elephant", "tiger", "rabbit", "rose", "snake",
        "engine", "echo", "orange", "anchor", "eagle", "igloo",
        "noodle", "exit", "tongue", "envelope", "umbrella",
        "antelope", "octopus", "sunrise", "evening", "globe",
        "blanket", "tree", "egg", "garden", "night", "tree",
        "honey", "yarn", "nail", "lake", "kettle",
    ]

    # First try seeds (fast, offline)
    candidates = [w for w in SEEDS if w.startswith(letter) and w not in used]
    if candidates:
        return random.choice(candidates)

    # Try the API to find a real word starting with `letter`
    # We query common letter-patterns hoping for a hit
    attempts = [letter + suffix for suffix in ["at", "an", "en", "in", "on", "est", "ight", "ound"]]
    for attempt in attempts:
        if attempt not in used and is_valid_word(attempt):
            return attempt

    return None  # Bot is genuinely stuck — player wins!


def reset_game():
    seed_words = ["apple", "orange", "tiger", "engine", "rabbit", "eagle"]
    start = random.choice(seed_words)
    st.session_state.current_word = start
    st.session_state.score = 0
    st.session_state.used = {start}
    st.session_state.message = ("info", f"Game started! First word is **{start}**.")
    st.session_state.game_over = False
    st.session_state.input_key = st.session_state.get("input_key", 0) + 1  # clears text input


# ── State init ────────────────────────────────────────────────────────────────
if "current_word" not in st.session_state:
    st.session_state.input_key = 0
    reset_game()

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🧠 Word Chain Game")
st.caption("Chain real English words — each word must start with the last letter of the previous one.")

col1, col2, col3 = st.columns(3)
col1.metric("Current word", st.session_state.current_word.upper())
col2.metric("Your score", st.session_state.score)
col3.metric("Words used", len(st.session_state.used))

st.divider()

# Message banner
msg_type, msg_text = st.session_state.get("message", ("info", ""))
if msg_text:
    getattr(st, msg_type)(msg_text)

if not st.session_state.game_over:
    required_letter = st.session_state.current_word[-1]
    st.write(f"Next word must start with: **{required_letter.upper()}**")

    user_word = st.text_input(
        "Your word",
        key=f"word_input_{st.session_state.input_key}",
        placeholder=f"Type a word starting with '{required_letter.upper()}'…",
    ).strip().lower()

    submit, _, reset_btn = st.columns([2, 5, 2])
    submitted = submit.button("Submit ✅", use_container_width=True)
    reset_btn.button("New game 🔄", on_click=reset_game, use_container_width=True)

    if submitted:
        # ── Validation ────────────────────────────────────────────────────────
        if not user_word:
            st.session_state.message = ("warning", "Please enter a word first!")

        elif user_word in st.session_state.used:
            st.session_state.message = ("error", f"**{user_word}** has already been used. Try another!")

        elif not user_word.startswith(required_letter):
            st.session_state.message = (
                "error",
                f"**{user_word}** doesn't start with **{required_letter.upper()}**. Try again!",
            )

        elif not is_valid_word(user_word):
            st.session_state.message = ("error", f"**{user_word}** isn't a recognised English word.")

        else:
            # ── Valid player move ─────────────────────────────────────────────
            st.session_state.score += 1
            st.session_state.used.add(user_word)
            st.session_state.current_word = user_word
            st.session_state.input_key += 1  # clears the text box

            # Bot's turn
            bot_letter = user_word[-1]
            bot_word = bot_pick(bot_letter, st.session_state.used)

            if bot_word is None:
                # Bot is stuck — player wins
                st.session_state.message = (
                    "success",
                    f"🎉 You win! I couldn't think of a word starting with "
                    f"**{bot_letter.upper()}**. Final score: **{st.session_state.score}**",
                )
                st.session_state.game_over = True
            else:
                st.session_state.used.add(bot_word)
                st.session_state.current_word = bot_word
                st.session_state.message = (
                    "info",
                    f"My word: **{bot_word}** — now you need a word starting with "
                    f"**{bot_word[-1].upper()}**",
                )

        st.rerun()

else:
    # Game over — just show restart
    if st.button("Play again 🔄", use_container_width=True):
        reset_game()
        st.rerun()

# ── Used words expander ───────────────────────────────────────────────────────
with st.expander("📜 Words used so far"):
    st.write(", ".join(sorted(st.session_state.used)))
