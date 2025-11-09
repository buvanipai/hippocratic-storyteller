import os
from dotenv import load_dotenv
from openai import OpenAI
import json

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
     # please use your own openai api key here.
    resp = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    stream=False,
    max_tokens=max_tokens,
    temperature=temperature)
    return resp.choices[0].message.content  # type: ignore


def generate_story(user_request: str, feedback: str = None) -> str:
    """Generates a story based on user request and optional judge feedback."""

    base_prompt = f"""
    You are a warm, imaginative children's author. Write a bedtime story for ages 5–10 based on the request below.

    USER REQUEST: {user_request}

    Write about 1200 words.

    Story shape:
    1) Opening: introduce the child character and ONE specific, concrete problem.
    2) Struggle: the character tries and fails a couple of times; show their thinking, small mistakes, and a change in approach.
    3) Resolution: the character succeeds using what they learned; the lesson is shown through actions, not explained.
    4) Ending: peaceful, warm, sleepy.

    Guidance:
    - Keep the plot centered on the obstacle and how it’s solved. No extra subplots.
    - Use vivid but simple sensory details (sounds, colors, textures).
    - Include 3–5 short lines of natural dialogue.
    - Show emotions through actions (e.g., hands shaking, a deep breath) instead of naming the emotion.
    - Keep it gentle and age-appropriate—no scary content.

    Examples of quiet lessons (show, don’t tell):
    - Trying again leads to success.
    - Asking for help turns a problem into a team effort.
    - Carefulness and patience fix what rushing broke.

    {('Incorporate this feedback from a prior attempt: ' + feedback) if feedback else ''}

    Write the complete story now.
    """

    return call_model(base_prompt, temperature=0.9)


def judge_story(story: str, user_request: str) -> dict:
    """Judge evaluates the story for quality and age-appropriateness."""

    judge_prompt = f"""
    You are a children's literature editor. Evaluate the story on the essentials for a great bedtime story.

    USER REQUEST: {user_request}
    STORY: {story}

    Score each 0–10 and justify briefly:
    1) CLEAR OBSTACLE: One specific problem drives the story. What is it?
    2) REAL STRUGGLE: Character tries and fails before succeeding; shows effort and learning.
    3) LESSON EMBEDDED: Lesson shown through actions (not told at the end). What is learned and how?
    4) PLOT MOMENTUM: Actions move the story forward (not just description).
    5) SENSORY DETAIL: Simple, vivid specifics (sounds, colors, textures).
    6) AGE-APPROPRIATE: Safe, gentle for ages 5–10.
    7) BEDTIME READY: Calming, warm ending.
    8) DIALOGUE: 3–5 natural lines that reveal character or move plot; count them.
    9) WORD COUNT: Aim ≈1200 words (acceptable 1000–1400).
    10) MAGIC & WONDER: Gentle imagination suitable for kids.

    Return JSON only:
        {{
        "reasoning": {{
            "obstacle": "<clear and concrete?>",
            "struggle": "<tries, fails, learns?>",
            "lesson": "<what and how?>",
            "plot": "<moves vs meanders?>",
            "sensory": "<specifics?>",
            "age": "<safe?>",
            "bedtime": "<calming?>",
            "dialogue": "<count + quality>",
            "word_count": "<approx count>",
            "magic": "<gentle wonder?>"
        }},
        "scores": {{
            "clear_obstacle": <0-10>,
            "real_struggle": <0-10>,
            "lesson_embedded": <0-10>,
            "plot_momentum": <0-10>,
            "sensory_detail": <0-10>,
            "age_appropriate": <0-10>,
            "bedtime_ready": <0-10>,
            "dialogue": <0-10>,
            "word_count": <0-10>,
            "magic_and_wonder": <0-10>
        }},
        "overall_score": <average of all scores>,
        "passes": <true if (scores.clear_obstacle>=8 and scores.real_struggle>=8 and scores.lesson_embedded>=8 and scores.age_appropriate>=9 and scores.word_count>=7)>,
        "feedback": "<Concrete fixes with brief quotes: clarify obstacle? add failed attempt? embed lesson in action? tighten ending?>"
        }}
    """

    response = call_model(judge_prompt, temperature=0.1)

    # Parse the JSON response
    try:
        # Extract JSON from the response (handle potential markdown formatting)
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()

        result = json.loads(json_str)
        return result
    except:
        # Fallback if JSON parsing fails
        return {
            "overall_score": 5,
            "passes": False,
            "feedback": "Story evaluation completed."
        }


def storytelling_system(user_request: str, max_iterations: int = 3) -> tuple[str]:
    """
    Main storytelling system with judge feedback loop
    Return: (final_story, final_evaluation)
    """

    print("\n --- Generating Initial Story ---\n")

    # First Attempt

    story = generate_story(user_request)
    evaluation = judge_story(story, user_request)

    print(f"Story quality score: {evaluation['overall_score']:.1f}/10")

    iteration = 1

    # Refinement Loop
    while not evaluation['passes'] and iteration < max_iterations:

        print(f"\n --- Refining story (iteration {iteration + 1}) ---\n")
        story = generate_story(user_request, evaluation['feedback'])
        evaluation = judge_story(story, user_request)

        print(f"Updated Score: {evaluation['overall_score']:.1f}/10")

        iteration += 1

    if evaluation['passes']:
        print("\nStory approved by judge!\n")
    else:
        print("\nStory complete (reached max iterations)\n")

    return story, evaluation

def get_user_feedback(story: str) -> str:
    """
    Allow user to request changes to the story.
    """
    print("\n" + "="*60)
    print("Would you like to add or change anything in the story?")
    print("(Examples: 'Make it funnier', 'Add a talking animal', 'Make it shorter', etc.)")
    print("Or press Enter to keep it as is.")
    print("="*60 + "\n")

    try:
        feedback = input("\nYour feedback: ").strip()
    except EOFError:
        feedback = ""
    return feedback


example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


def main():
    print("="*60)
    print("\nWelcome to the Bedtime Story Generator!")
    print("="*60)
    print("\nI can create magical bedtime stories for children ages 5-10 based on your requests.")
    print("\nExamples:")
    print("   - A story about a brave mouse who explores a castle.")
    print("   - Tell me about a friendship between a girl and a dragon.")
    print("   - A story about a boy who finds a magic paintbrush.")
    print("="*60)

    user_input = input("What kind of story do you want to hear? ").strip()

    if not user_input:
        user_input = example_requests
        print(f"\nUsing example request: {user_input}\n")

    # Generate story with judge feedback
    story, evaluation = storytelling_system(user_input)

    # Display the story
    print("\n" + "="*60)
    print("YOUR BEDTIME STORY")
    print("="*60 + "\n")
    print(story)
    print("\n" + "="*60)

    # Optional: Allow user to request up to three refinements
    max_user_revisions = 3
    for i in range(max_user_revisions):
        user_feedback = get_user_feedback(story)
        if not user_feedback:
            break
        print("\nCreating a revised version based on your feedback...\n")
        revised_request = f"{user_input}. User also requested: {user_feedback}"
        story, evaluation = storytelling_system(revised_request)
        print("\n" + "="*60)
        print(f"REVISION {i+1}")
        print("="*60 + "\n")
        print(story)
        print("\n" + "="*60)

    print("\nThank you for using the Bedtime Story Generator! Sweet dreams!\n")


if __name__ == "__main__":
    main()