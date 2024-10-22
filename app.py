from flask import Flask, render_template, request, jsonify
import random
import string
import nltk
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')  # Téléchargement de punkt pour le tokeniseur
app = Flask(__name__)

# Load your pre-processed tokens
try:
    with open('answers.pkl', 'rb') as f:
        sent_tokens = pickle.load(f)
except FileNotFoundError:
    print("sent_tokens.pkl not found. Please create it first.")
    sent_tokens = []  # Si le fichier n'existe pas, initialise une liste vide

# Initialize the lemmatizer
lemmer = nltk.stem.WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

# Updated greeting inputs and responses
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey", "howdy", "yo", "hi there", "salutations")
GREETING_RESPONSES = [
    "Hi! Are you interested in AI or Data Science fields?",
    "Hey there! How can I assist you with AI or Data Science today?",
    "Welcome! Do you have any questions about AI or Data Science?",
    "Hello! I'm excited to chat with you about AI and Data Science!",
    "Hi! Feel free to ask me anything related to AI or Data Science.",
    "Greetings! What topics in AI or Data Science are you curious about?",
    "Hey! Let's dive into the world of AI and Data Science together!",
    "Hi there! What would you like to learn more about in AI or Data Science?",
    "Hello! I'm here to help with any questions you have about AI or Data Science!",
    "Hi! It's great to connect with you. How can I help you in AI or Data Science?"
]

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def response(user_response):
    robo_response = ''

    # Normaliser la réponse de l'utilisateur
    user_response_normalized = ' '.join(LemNormalize(user_response))
    
    # Ajouter l'entrée de l'utilisateur à sent_tokens pour le TF-IDF
    sent_tokens.append(user_response_normalized)

    # Créer le modèle TF-IDF
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)

    # Calculer la similarité cosinus
    vals = cosine_similarity(tfidf[-1], tfidf[:-1])  # Comparer uniquement avec les entrées précédentes
    idx = vals.argsort()[0][-1]  # Obtenir l'indice de la réponse la plus proche

    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-1]

    if req_tfidf == 0:
        robo_response = "I am sorry! I don't understand you."
    else:
        # Renvoie uniquement la réponse associée, sans répéter la question
        robo_response = sent_tokens[idx]

    # Enlever l'entrée de l'utilisateur pour ne pas l'inclure dans les futures réponses
    sent_tokens.pop()

    return robo_response


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["msg"]
    user_input = user_input.lower()

    if user_input == 'bye':
        return jsonify({"response": "Bye! Take care.."})

    if greeting(user_input) is not None:
        return jsonify({"response": greeting(user_input)})

    else:
        return jsonify({"response": response(user_input)})

if __name__ == "__main__":
    app.run(debug=True)
