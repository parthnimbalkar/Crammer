import os
import streamlit as st
import requests
import re
import html

# Check if running on Streamlit Cloud or locally
if hasattr(st, 'secrets') and 'API_URL' in st.secrets:
    API_URL = st.secrets["API_URL"]
else:
    API_URL = os.getenv("API_URL", "http://localhost:8000")

def parse_flashcards(flashcard_text: str) -> list:
    """
    Parse the LLM-generated flashcard text into structured data
    """
    cards = []
    
    if not flashcard_text or len(flashcard_text) < 10:
        return []
    # Split by "Card X:" pattern
    card_pattern = r'Card \d+:'
    card_sections = re.split(card_pattern, flashcard_text)
    for idx, section in enumerate(card_sections):
        if not section.strip():
            continue
        # Extract Front and Back
        front_match = re.search(r'Front:\s*(.+?)(?=Back:)', section, re.DOTALL)
        back_match = re.search(r'Back:\s*(.+?)(?=$|Card)', section, re.DOTALL)
        if front_match and back_match:
            front = front_match.group(1).strip()
            back = back_match.group(1).strip()
            cards.append({"front": front, "back": back})
    return cards
    
    return cards


def show_flashcards_interface():
    """
    Render the flashcards interface with card flipping
    """
    st.markdown("### 🗂️ Flashcard Mode")
    st.markdown("Generate and review flashcards from your study materials.")
    st.markdown("---")
    
    # Initialize session state
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    if "known_cards" not in st.session_state:
        st.session_state.known_cards = set()
    
    # ========== GENERATION SECTION ==========
    if not st.session_state.flashcards:
        st.markdown("#### 🎯 Generate Flashcards")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            topic = st.text_input(
                "What topic would you like flashcards on?",
                placeholder="Enter a topic from your uploaded documents"
                )
        
        with col2:
            num_cards = st.number_input(
                "Number of cards",
                min_value=5,
                max_value=30,
                value=10,
                step=5
            )
        
        if st.button("🎴 Generate Flashcards", type="primary", use_container_width=True):
            if not topic:
                st.warning("⚠️ Please enter a topic first!")
            else:
                with st.spinner("📄 Generating flashcards..."):
                    try:
                        
                        response = requests.post(
                            f"{API_URL}/flashcards",
                            json={
                                "topic": topic,
                                "num_cards": num_cards
                            },
                            timeout=60
                        )
                        

                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success"):
                                data = result["data"]
                                flashcard_text = data.get("flashcards", "")
                                

                                
                                # Parse flashcards
                                cards = parse_flashcards(flashcard_text)
                                
                                if cards:
                                    st.session_state.flashcards = cards
                                    st.session_state.current_card_index = 0
                                    st.session_state.show_answer = False
                                    st.session_state.known_cards = set()
                                    st.success(f"✅ Generated {len(cards)} flashcards!")
                                    st.rerun()
                                else:
                                    st.error("❌ Could not parse flashcards. Check debug info above.")
                            else:
                                st.error(f"❌ Backend error: {result.get('error')}")
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                            st.code(response.text)
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. Try with fewer cards.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend. Is it running on port 8000?")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # Tips
        st.markdown("---")
        st.markdown("##### 💡 Tips:")
        st.markdown("""
        - Be specific with your topic for better flashcards
        - Start with 10 cards and generate more if needed
        - Cards are generated from your uploaded documents
        """)
    
    # ========== FLASHCARD REVIEW SECTION ==========
    else:
        cards = st.session_state.flashcards
        current_idx = st.session_state.current_card_index
        current_card = cards[current_idx]
        
        # Progress bar
        progress = (current_idx + 1) / len(cards)
        st.progress(progress, text=f"Card {current_idx + 1} of {len(cards)}")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cards", len(cards))
        with col2:
            st.metric("Known", len(st.session_state.known_cards))
        with col3:
            remaining = len(cards) - len(st.session_state.known_cards)
            st.metric("To Review", remaining)
        
        st.markdown("---")
        
        # Get the content to display
        display_text = current_card['front'] if not st.session_state.show_answer else current_card['back']
        display_title = '❓ Question' if not st.session_state.show_answer else '✅ Answer'
        
    
        
        # Flashcard Display - Use st.markdown instead of HTML
        st.markdown(f"### {display_title}")
        
        # Display the card content in a nice container
        st.markdown(
            f"""
            <div style="
                background: black;
                padding: 2rem;
                border-radius: 15px;
                border: 3px solid #1f77b4;
                min-height: 200px;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <p style="font-size: 1.2rem; line-height: 1.6; color: white; margin: 0;">
                    {html.escape(display_text)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("")
        
        # Flip Button
        if not st.session_state.show_answer:
            if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        
        # Action Buttons (shown after flip)
        if st.session_state.show_answer:
            st.markdown("#### How well did you know this?")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("❌ Don't Know", use_container_width=True):
                    st.session_state.known_cards.discard(current_idx)
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with col2:
                if st.button("🤔 Review Again", use_container_width=True):
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    st.rerun()
            
            with col3:
                if st.button("✅ Know It!", use_container_width=True, type="primary"):
                    st.session_state.known_cards.add(current_idx)
                    st.session_state.show_answer = False
                    if current_idx < len(cards) - 1:
                        st.session_state.current_card_index += 1
                    else:
                        st.balloons()
                    st.rerun()
        
        # Navigation
        st.markdown("---")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        
        with nav_col1:
            if st.button("⬅️ Previous", disabled=(current_idx == 0)):
                st.session_state.current_card_index -= 1
                st.session_state.show_answer = False
                st.rerun()
        
        with nav_col2:
            # Jump to card
            card_options = [f"Card {i+1}" for i in range(len(cards))]
            selected = st.selectbox(
                "Jump to card:",
                card_options,
                index=current_idx,
                label_visibility="collapsed"
            )
            new_idx = card_options.index(selected)
            if new_idx != current_idx:
                st.session_state.current_card_index = new_idx
                st.session_state.show_answer = False
                st.rerun()
        
        with nav_col3:
            if st.button("Next ➡️", disabled=(current_idx == len(cards) - 1)):
                st.session_state.current_card_index += 1
                st.session_state.show_answer = False
                st.rerun()
        
        # Bottom Actions
        st.markdown("---")
        bottom_col1, bottom_col2, bottom_col3 = st.columns(3)
        
        with bottom_col1:
            if st.button("🔙 Back to Home"):
                st.session_state.current_page = "home"
                st.rerun()
        
        with bottom_col2:
            if st.button("🔄 Generate New"):
                st.session_state.flashcards = []
                st.session_state.current_card_index = 0
                st.session_state.show_answer = False
                st.session_state.known_cards = set()
                st.rerun()
        
        with bottom_col3:
            if st.button("🗑️ Clear Cards"):
                st.session_state.flashcards = []
                st.session_state.current_card_index = 0
                st.session_state.show_answer = False
                st.session_state.known_cards = set()
                st.rerun()
        
        # Show completion message
        if len(st.session_state.known_cards) == len(cards):
            st.success("🎉 Congratulations! You've marked all cards as known!")