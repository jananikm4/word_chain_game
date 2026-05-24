import streamlit as str
import random
import requests
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Word Chain Game Extreme", page_icon="🧠", layout="centered")

# Custom CSS for modern styling and smooth visual elements
st.markdown("""
    <style>
    .word-card {
        background-color: #1E293B;
        border: 2px solid #38BDF8;
        border-radius: 8px;
        padding: 6px 12px;
        margin: 4px;
        display: inline-block;
        font-weight: bold;
        color: #F8FAFC;
    }
    .arrow {
        color: #94A3B8;
        font-size: 1.2rem;
        margin: 0 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def is_valid_word(word: str) -> bool:
    """Validate against Free Dictionary API."""
    try:
        r = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=2,
        )
        return r.status_code == 200
    except requests.RequestException:
        return True  # Fallback gracefully during network glitches


def bot_pick(letter: str, used_list: list) -> str | None:
    """Finds a valid response word starting with the required letter."""
    SEEDS = [
        "apple", "elephant", "tiger", "rabbit", "rose", "snake",
        "engine", "echo", "orange", "anchor", "eagle", "igloo",
        "noodle", "exit", "tongue", "envelope", "umbrella",
        "antelope", "octopus", "sunrise", "evening", "globe",
        "blanket", "tree", "egg", "garden", "night", "honey", 
        "yarn", "nail", "lake", "kettle", "zebra", "queen", "xylophone", "jacket"
    ]

    used_set = set(used_list)
    candidates = [w for w in SEEDS if w.startswith(letter) and w not in used_set]
    if candidates:
        return random.choice(candidates)

    attempts = [letter + suffix for suffix in ["at", "an", "en", "in", "on", "est", "ight", "ound", "ero", "one"]]
    for attempt in attempts:
        if attempt not in used_set and is_valid_word(attempt):
            return attempt

    return None


def calculate_points(word: str) -> tuple[int, bool]:
    """Calculates points with a 3x multiplier for rare letters."""
    base_points = len(word)
    rare_letters = {'z', 'q', 'x', 'j', 'k'}
    
    # Check if the word starts or ends with a high-value rare letter
    if word[0] in rare_letters or word[-1] in rare_letters:
        return base_points * 3, True
    return base_points, False


def reset_game():
    seed_words = ["apple", "orange", "tiger", "engine", "rabbit", "eagle"]
    start = random.choice(seed_words)
    st.session_state.current_word = start
    st.session_state.score = 0
    st.session_state.used = [start]
    st.session_state.message = ("info", f"💥 Game started! First word is **{start.upper()}**.")
    st.session_state.game_over = False
    st.session_state.skips_left = 1
    st.session_state.freezes_left = 1
    st.session_state.freeze_active = False
    st.session_state.start_time = time.time()
    st.session_state.input_key = st.session_state.get("input_key", 0) + 1


# ── State Init & Safety Checks ────────────────────────────────────────────────
if "high_score" not in st.session_state:
    st.session_state.high_score = 0

if "current_word" not in st.session_state or "freeze_active" not in st.session_state:
    st.session_state.input_key = 0
    reset_game()

# ── Dynamic Timer Check ───────────────────────────────────────────────────────
TURN_LIMIT = 20  # Seconds allowed per turn

if not st.session_state.game_over and not st.session_state.freeze_active:
    elapsed = time.time() - st.session_state.start_time
    time_remaining = max(0, int(TURN_LIMIT - elapsed))
    if time_remaining <= 0:
        st.session_state.game_over = True
        st.session_state.message = ("error", f"⏱️ **Time's up!** You didn't answer within {TURN_LIMIT} seconds. Game Over!")
else:
    time_remaining = TURN_LIMIT

# ── UI Layout ─────────────────────────────────────────────────────────────────
st.title("🧠 Word Chain Game Extreme")
st.caption("Chain English words together. Watch out for the clock and maximize points with rare letters!")

# Game stats panel
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Word", st.session_state.current_word.upper())
col2.metric("Your Score", st.session_state.score)
col3.metric("🏆 High Score", st.session_state.high_score)
col4.metric("Words Chain Length", len(st.session_state.used))

# Timer & Power-ups Dashboard
dash_col1, dash_col2, dash_col3 = st.columns([2, 1, 1])

if not st.session_state.game_over:
    if st.session_state.freeze_active:
        dash_col1.markdown("⏱️ **Timer:** ❄️ *FROZEN*")
    else:
        # Dynamic color changing depending on urgency
        timer_color = "red" if time_remaining <= 5 else "orange" if time_remaining <= 10 else "green"
        dash_col1.markdown(f"⏱️ **Timer:** :{timer_color}[{time_remaining}s remaining]")
else:
    dash_col1.markdown("⏱️ **Timer:** Stop")

# Power-up Buttons
if dash_col2.button(f"🛡️ Skip ({st.session_state.skips_left})", disabled=st.session_state.skips_left <= 0 or st.session_state.game_over, use_container_width=True):
    st.session_state.skips_left -= 1
    # Generate an entirely fresh word context
    fresh_seeds = ["zebra", "quantum", "galaxy", "matrix", "velvet", "whisper"]
    new_start = random.choice(fresh_seeds)
    st.session_state.current_word = new_start
    st.session_state.used.append(new_start)
    st.session_state.start_time = time.time()
    st.session_state.message = ("warning", f"🛡️ Turn skipped! Fresh start word is **{new_start.upper()}**")
    st.session_state.input_key += 1
    st.rerun()

if dash_col3.button(f"❄️ Freeze ({st.session_state.freezes_left})", disabled=st.session_state.freezes_left <= 0 or st.session_state.game_over or st.session_state.freeze_active, use_container_width=True):
    st.session_state.freezes_left -= 1
    st.session_state.freeze_active = True
    st.session_state.message = ("info", "❄️ Time Frozen for this turn! Take your time to think.")
    st.rerun()

st.divider()

# Process Feedback Banner
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
    
    # Rare letter visual warning indicator
    if required_letter in ['Z', 'Q', 'X', 'J', 'K']:
        st.markdown(f"Next word must start with: **:orange[{required_letter}]** 🔥 **3x MULTIPLIER ACTIVE!**")
    else:
        st.markdown(f"Next word must start with: **{required_letter}**")

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
        if not user_word:
            st.session_state.message = ("warning", "⚠️ Please enter a word first!")
            st.rerun()

        elif user_word in st.session_state.used:
            st.session_state.message = ("error", f"❌ **{user_word.upper()}** has already been used. Try another!")
            st.rerun()

        elif not user_word.startswith(required_letter.lower()):
            st.session_state.message = ("error", f"❌ **{user_word.upper()}** doesn't start with **{required_letter}**. Try again!")
            st.rerun()

        elif not is_valid_word(user_word):
            st.session_state.message = ("error", f"❌ **{user_word.upper()}** isn't a recognized English dictionary word.")
            st.rerun()

        else:
            # Valid player move calculation
            gained_points, multiplied = calculate_points(user_word)
            st.session_state.score += gained_points
            st.session_state.used.append(user_word)
            st.session_state.current_word = user_word
            st.session_state.input_key += 1 
            st.session_state.freeze_active = False # Unfreeze timer context if active

            # Trigger celebration on high-score breakthroughs
            if st.session_state.score > st.session_state.high_score and st.session_state.high_score > 0:
                st.balloons()
            
            if st.session_state.score > st.session_state.high_score:
                st.session_state.high_score = st.session_state.score

            # Bot counter-attack step
            bot_letter = user_word[-1]
            bot_word = bot_pick(bot_letter, st.session_state.used)

            if bot_word is None:
                st.session_state.message = (
                    "success",
                    f"🎉 **You win!** I couldn't find an available word starting with **{bot_letter.upper()}**. Final score: **{st.session_state.score}**",
                )
                st.session_state.game_over = True
            else:
                st.session_state.used.append(bot_word)
                st.session_state.current_word = bot_word
                bonus_msg = " 🔥 [RARE MULTIPLIER 3x!]" if multiplied else ""
                st.session_state.message = (
                    "success" if multiplied else "info",
                    f"Nice word (+{gained_points} pts){bonus_msg}! My counter word is **{bot_word.upper()}** — next word needs to start with **{bot_word[-1].upper()}**",
                )
            
            # Reset countdown timer for the next turn loop
            st.session_state.start_time = time.time()
            st.rerun()

else:
    # Game over display screen
    st.markdown("### 🛑 Game Over")
    if st.button("Play Again 🔄", use_container_width=True):
        reset_game()
        st.rerun()

# ── Custom Visual Word Chain History ──────────────────────────────────────────
st.write("")
with st.expander("📜 Word Chain History Visualized", expanded=True):
    if st.session_state.used:
        chain_html = ""
        for i, w in enumerate(st.session_state.used):
            chain_html += f'<span class="word-card">{w.upper()}</span>'
            if i < len(st.session_state.used) - 1:
                chain_html += '<span class="arrow">➔</span>'
        st.markdown(chain_html, unsafe_allow_html=True)
    else:
        st.info("No words logged yet.")

# Auto-rerun loop to smoothly keep the countdown timer ticking live down to the second
if not st.session_state.game_over and not st.session_state.freeze_active:
    time.sleep(1)
    st.rerun()
