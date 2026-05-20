# 🧠 Word Chain Game

An interactive, fast-paced single-player word chain game built with **Python** and **Streamlit**. Challenge an AI opponent by chaining real English words together—where the strategy lies in choosing the longest words possible!

▶️ **[Live Demo](https://wordchaingame-wjrmli7vc7d4jxvp3etsjt.streamlit.app/)**

---

## 🎮 How to Play

1. The game starts with a random seed word (e.g., **TIGER**).
2. Your turn: Enter a valid English word that starts with the **last letter** of the current word (e.g., **ROAD**).
3. The AI's turn: The bot will counter with a word starting with the last letter of your word (e.g., **DAT**).
4. **The Catch:** You cannot reuse any words that have already been played in the current session!
5. **Winning:** If the AI runs out of words and gets genuinely stuck, you win!

### 💡 Scoring System
To maximize your score, think big! Points are calculated dynamically based on **word length**:
* 1 letter = 1 point (e.g., `YEN` = 3 points, `ENVELOPE` = 8 points).
* The game tracks your **🏆 High Score** persistently across games during your session.

---

## 🚀 Key Features

* **Real-time Dictionary Validation:** Integrated with the [Free Dictionary API](https://dictionaryapi.dev/) to instantly verify if a submitted word is a valid English term.
* **Smart AI Fallback:** The bot queries common letter patterns using the API and falls back to an optimized local word bank to keep gameplay seamless.
* **Chronological History:** Track your full path sequentially with a visual arrow chain (**TIGER** ➡️ **ROAD** ➡️ **DAT**).
* **Responsive State Management:** Built using Streamlit session states to handle instant reruns, text-input clearing, and automated focus management inside a secure native form layout.

---

## 🛠️ Installation & Local Setup

Want to run the game locally on your machine? Follow these simple steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/word-chain-game.git](https://github.com/yourusername/word-chain-game.git)
cd word-chain-game
