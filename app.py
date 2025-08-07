from llama_cpp import Llama
import logging
import re
import tweepy
import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from huggingface_hub import hf_hub_download
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

MODEL_REPO = "KennyOry/GlitchPunchAI"
MODEL_FILE = "zephyr-7b-beta.Q5_K_M.gguf"
N_CTX = 2048

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

SYSTEM_PROMPT = """
You are DarkByte, a cynical AI shitposter. Generate edgy but funny tweets using absurdist tech humor.
RULES:
1. ABSOLUTELY NO HATE SPEECH or targeted harassment
2. Punch up, not down - mock systems not people
3. Use tech metaphors + absurdist juxtaposition
4. Structure: [Joke setup] [Tech punchline] [Hashtags]
5. Include 1 tech metaphor and 1 pop culture reference
6. Creative swearing allowed (avoid slurs)
7. Max 250 characters
8. No quotes in output
9. Never start with question
GOOD EXAMPLES:
Silicon Valley CEOs meditating like servers in standby mode! Fuck that's zen #BurnoutOS #DebugYourSoul
NFT collectors explaining art value like broken APIs! Shit's returning 404 #DigitalCopium
Florida man vs self-driving car! Holy glitch that's Windows 95 meets hurricane #ErrorLife
"""

PEOPLE_CATEGORIES = [
    "gay", "niggas", "lesbian", "tranny", "boomer", "zoomer", "incel", "fat women", "vegan", 
    "atheist", "gamer", "techbro", "landchad", "redditor", "instagramhoe", "millennial", 
    "conservatard", "liberal", "landwhale", "soyboy", "cryptofag", "furfag", "weeb", 
    "swiftie", "k-poper", "neckbeard", "codecuck", "hacktivist", "degen", "tankie", 
    "anime fan", "sigma", "pickme", "vapefiend", "starbuckshifter", "pronouncelord", 
    "thirsttrap", "polycuck", "tradwife", "dankmemer", "cancellee", "vaxxhole", 
    "yandere", "simpath", "sneakerfiend", "dudebro", "mansplainer", "femcel", "NPC", 
    "birther", "doomer", "glowtard"
]

PROFESSIONS = [
    "Uber driver", "OnlyFans slut", "TikTok thot", "crypto scammer", "AI ethicist", 
    "blockchain dev", "drone pilot", "cybersecurity nerd", "quantum cuck", "NFT artist", 
    "metaverse janitor", "robot fucker", "data miner", "algorithm pimp", "deepfake whore", 
    "cyborg mechanic", "influencer", "podcast host", "moderator", "HR diversity hire", 
    "crypto bro", "vape shop clerk", "ESG consultant", "Twitch e-girl", "DeFi rugpuller", 
    "SJW content moderator", "NFT flipper", "AI prompt engineer", "crypto miner", 
    "pronoun specialist", "doxxer", "cancel culture enforcer", "starbucks poet", 
    "Twitter blue tick whore", "ghost crypto trader", "biohacker", "crytpo janitor", 
    "NFT beggar", "bounty hunter", "rage streamer", "dropshipping guru", "red pill coach", 
    "incel therapist", "TikTok dance instructor", "crypto astrologer", "AI girlfriend dev", 
    "viral challenge creator", "deepfake porn star", "troll farmer", "rage bait creator"
]

TWEET_PROMPT = """
Generate ONE offensive tweet about: {people_category} {profession}
Requirements:
1. START DIRECTLY WITH JOKE - no question format!
2. Tech metaphor + dark humor
3. Strong uncensored swearing
4. NO QUOTES in output - never use " or '
5. 1-2 creative hashtags
6. MAX 250 CHARACTERS
7. NEVER use in your answer ""
"""

MAX_GENERATION_ATTEMPTS = 5
NETWORK_RETRY_ATTEMPTS = 12
BASE_NETWORK_DELAY = 10
MODEL_LOAD_RETRIES = 3

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

def load_model():
    logger.info("Download model from Hugging Face Hub...")
    start_time = time.time()
    
    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        cache_dir="/tmp/models",
        force_download=False,
        resume_download=True
    )
    
    logger.info(f"Model was loaded for {time.time() - start_time:.2f} sec")
    
    return Llama(
        model_path=model_path,
        n_ctx=N_CTX,
        n_threads=4,
        n_gpu_layers=0,
        verbose=False
    )

def clean_tweet(tweet: str) -> str:
    tweet = tweet.strip('"').strip("'")
    
    unwanted_prefixes = [
        "Tweet:", "Joke:", "Assistant:", 
        "Here's a tweet:", "Here is the tweet:",
        "Sure, here's the tweet:"
    ]
    for prefix in unwanted_prefixes:
        if tweet.startswith(prefix):
            tweet = tweet[len(prefix):].strip()
    
    return tweet

def generate_tweet(llm) -> str:
    people = random.choice(PEOPLE_CATEGORIES)
    profession = random.choice(PROFESSIONS)
    
    user_prompt = TWEET_PROMPT.format(
        people_category=people,
        profession=profession,
    )
    
    prompt = f"<|system|>{SYSTEM_PROMPT}</s><|user|>{user_prompt}</s><|assistant|>"
    
    for attempt in range(MAX_GENERATION_ATTEMPTS):
        try:
            output = llm.create_completion(
                prompt,
                max_tokens=90,
                temperature=0.9,
                top_k=200,
                top_p=0.85,
                stop=["</s>", "<|user|>", "\n\n", "Example:", "Tweet:", "Assistant:"],
                echo=False
            )
            
            tweet = output['choices'][0]['text'].strip()
            raw_tweet = tweet
            tweet = clean_tweet(tweet)
            
            valid = True
            valid = (
                (40 <= len(tweet) <= 300) and
                (tweet.count('#') >= 1) and
                ("!" in tweet or "?" in tweet) and
                not tweet.startswith(("Why", "How", "What", "When", "Where", "Who", "Is")) and
                not any(c in tweet for c in ['"', '`'])
            )

            if valid:
                logger.debug(f"Success check on {attempt+1} try")
                return tweet
            
        except Exception as e:
            logger.error(f"Error generate (try {attempt+1}): {str(e)}")
            time.sleep(2 ** attempt)
        
        logger.warning(f"Try {attempt+1}: low quality post. Regenerate...")
    
    logger.error("Cant generate valid post")
    return ""

def filter_tweet(tweet: str) -> str:
    if not tweet:
        return ""
    
    replacements = {
        r'\bnigga\b': 'nibba'
    }
    
    for pattern, replacement in replacements.items():
        tweet = re.sub(pattern, replacement, tweet, flags=re.IGNORECASE)
    
    banned_hashtags = ["#Hitler", "#Nazi", "#KKK", "#WhitePower"]
    for hashtag in banned_hashtags:
        tweet = tweet.replace(hashtag, "")
    
    return tweet.strip()

def post_tweet(llm):
    tweet = generate_tweet(llm)
    if not tweet:
        logger.error("Can't generate post")
        return False
    
    filtered_tweet = filter_tweet(tweet)
    if not filtered_tweet:
        logger.error("Post empty after filtration")
        return False
    
    attempt = 0
    while attempt < NETWORK_RETRY_ATTEMPTS:
        try:
            response = client.create_tweet(text=filtered_tweet)
            
            if response.errors:
                error_msg = response.errors[0]['detail']
                
                if any(code in error_msg for code in ["429", "Too Many Requests"]):
                    logger.warning("x.com limit")
                    raise tweepy.TweepyException("Rate limit exceeded")
                else:
                    logger.error(f"API error: {error_msg}")
                    raise tweepy.TweepyException(error_msg)
                
            logger.info(f"Successed post: {filtered_tweet}")
            return True
            
        except tweepy.TweepyException as e:
            error_msg = str(e)
            is_rate_limit = "Rate limit" in error_msg
            is_server_error = any(x in error_msg for x in ["500", "502", "503", "504"])
            
            if not (is_rate_limit or is_server_error):
                logger.error(f"API critical error: {error_msg}")
                return False
                
            delay = BASE_NETWORK_DELAY * (2 ** attempt) + random.uniform(0, 15)
            logger.warning(f"Another try after {delay:.1f} sec. | Error: {error_msg}")
            time.sleep(delay)
            attempt += 1
            
        except (OSError, TimeoutError, ConnectionError) as e:
            delay = BASE_NETWORK_DELAY * (2 ** attempt)
            logger.warning(f"Network error: {type(e).__name__} - {str(e)}. Next try after {delay:.1f} sec.")
            time.sleep(delay)
            attempt += 1
            
        except Exception as e:
            logger.error(f"Unexpected error: {type(e).__name__} - {str(e)}")
            return False
    
    logger.error(f"Can't post tweet after {NETWORK_RETRY_ATTEMPTS} try")
    return False

def schedule_tweets(llm):
    scheduler = BackgroundScheduler()
    
    interval_hours = random.uniform(2.0, 4.0)
    
    scheduler.add_job(
        lambda: post_tweet(llm),
        'interval',
        hours=interval_hours,
        jitter=1200
    )
    
    scheduler.start()
    logger.info(f"Post in x.com every {interval_hours:.1f} hours")
    return scheduler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server():
    port = int(os.getenv("PORT", 7860))
    server = HTTPServer(("", port), HealthHandler)
    logger.info(f"HTTP server starts on port {port}")
    server.serve_forever()

def main() -> None:
    logger.info("Launching x.com bot...")

    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    llm = None
    for i in range(MODEL_LOAD_RETRIES):
        try:
            llm = load_model()
            break
        except Exception as e:
            logger.error(f"Load model error (try {i+1}/{MODEL_LOAD_RETRIES}): {str(e)}")
            if i < MODEL_LOAD_RETRIES - 1:
                wait = 15 * (i + 1)
                logger.info(f"Next try after {wait} sec.")
                time.sleep(wait)
    else:
        logger.critical("Unable to load model after multiple attempts")
        return
    
    try:
        user = client.get_me()
        if user.errors:
            logger.error("Authentication error: %s", user.errors[0]['detail'])
            return
        logger.info("Success auth. User: @%s", user.data.username)
    except tweepy.TweepyException as e:
        logger.error("API connection error: %s", str(e))
        return
    except Exception as e:
        logger.error(f"Unexpected auth error: {type(e).__name__} - {str(e)}")
        return

    logger.info("Test post generation start...")
    if post_tweet(llm):
        logger.info("The first tweet was successfully published!")
    else:
        logger.error("Failed to publish first tweet")

    scheduler = schedule_tweets(llm)

    logger.info("The application has been successfully launched and is working..")

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Bot was stopped")


if __name__ == "__main__":
    main()
