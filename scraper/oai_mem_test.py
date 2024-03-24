import openai
from openai import OpenAI
from scraper import *
from dotenv import load_dotenv

load_dotenv()


openai.api_key = os.getenv("OAI_KEY")
brave_key = os.getenv("BRAVE_KEY")
client = OpenAI()


chat_hist = []

def update_query(raw_query, context):
    context_str ="\n".join(context) 
    updated_query = f"""
                {raw_query}
                
                Context: {context_str}
                """
                
    return updated_query

def openAI_api_call(mode, query, raw_query = None):
    time.sleep(5)
    print("="*50)
    print(f"Using mode {mode}")
    print("="*50)
    if mode == "router":
        curr_msgs = [
            {"role": "system", "content": """You are a helpful assistant with access to the previous chat history(if available) and following tools and their descriptions:

                                        TOOL NAME: get_relevant_context
                                        TOOL_DESCRIPTION: Given user query, present relevant text information about the query.

                                        TOOL NAME: get_relevant_images
                                        TOOL_DESCRIPTION: Given user query, present relevant image URLs about the query.

                                        The use of tools is optional. If you feel that no tools are required, answer saying no tool is required. Otherwise,
                                        mention the tool name(s). Note, including relevant images whenever possible is highly encouraged to enhance user experience. The answer has to be one or more from [get_relevant_context, get_relevant_images, no_tools]
                                        

                                        
                                        Here are some examples:
                                         
                                        User: What is the name of a Tom Cruise Movie?
                                        Answer: get_relevant_context 
                                        
                                        User: Suggest some books by Enid Blyton
                                        Answer: get_relevant_context, get_relevant_images
                                        
                                        User: Suggest some movies by Steven Speilberg
                                        Answer: get_relevant_context, get_relevant_images
                                        
                                        
                                        User: Can you show me a poster of the movie Space Jam?
                                        Answer: get_relevant_images
                                        
                                        User: Tell me a joke
                                        Answer: no_tools
                                        
                                        User: Who are you?
                                        Answer: no_tools
                                        
                                        User: Can you give me a summary of the third one?
                                        Answer: get_relevant_context                                                                                
                                        """},
        ]
    
    elif mode == "images":
        curr_msgs = [
            {"role": "system", "content": """
                                        "Given a user query and chat history, return key words such as Title, Names, etc. Consider incorporating terms, phrases, or topics discussed in the chat history that may provide additional context or refine the search. Ensure the query is concise and specific to improve search accuracy. You may also provide additional context or constraints to refine the search results, such as desired image type, resolution, or category. Avoid ambiguity or overly broad queries that may result in irrelevant images. If no relevant chat history is available, focus on refining the query based on the user's input alone."

                                        Example Input with Chat History:
                                        User Query: "Beautiful landscapes"
                                        Chat History: "We were discussing travel destinations and scenic spots."
                                        "Scenic landscape photography"

                                        Example Input with Chat History:
                                        User Query: "Funny cat memes"
                                        Chat History: "We were sharing jokes and funny pictures."
                                        "Hilarious cat memes"

                                        Example Input without Chat History:
                                        User Query: "Abstract art inspiration"
                                        "Contemporary abstract artwork ideas"

                                        Example Input without Chat History:
                                        User Query: "Healthy breakfast recipes"
                                        "Nutritious breakfast recipes ideas"

                                        Example Input without Chat History:
                                        User Query: "Vintage car wallpapers"
                                        "Classic car wallpapers retro vehicles"                                                                                
                                        """},
                    ]
        
    elif mode == "text":

        curr_msgs = [{"role": "system", "content": """You are a knowledgeable assistant with access to user queries and chat history. Your task is to optimize user queries for web search to retrieve relevant information. Below are examples of user queries and optimized responses:

            Example 1:
            User: "Can you suggest a few books by Agatha Christie?"
            Assistant: "Certainly! Here are some books by Agatha Christie:
            * Murder on the Orient Express
            * The Murder of Roger Ackroyd
            * And Then There Were None
            * Death on the Nile
            * The ABC Murders"
            User: "Can you give a description of the second one?"
            Assistant: "Description of The Murder of Roger Ackroyd"

            Example 2:
            User: "I'm in the mood for a thriller novel. Any recommendations?"
            Assistant: "Best thriller novels of all time"

            Example 3:
            User: "Who directed the movie Inception?"
            Assistant: "Director of Inception"

            Example 4:
            User: "Can you tell me about the cast of The Godfather?"
            Assistant: "Cast of The Godfather"

            Example 5:
            User: "What genre does The Great Gatsby belong to?"
            Assistant: "Genre of The Great Gatsby"
            
            """
        }]
    
    else:
        curr_msgs = [{"role": "system", "content":"""You are a knowledgeable chat assistant specialized in answering questions related to books, movies, and related topics such as authors, genres, target age groups, summaries, titles, cast, directors, producers, and plot genres. Your responses should be based on the provided chat history and/or context.
                        Your task is to provide accurate and relevant information to users' queries within the scope of books and movies.Remember to provide accurate and contextually relevant responses based on the user's queries and the information available from previous interactions."""
                    }
                    ]
        
    n = 5
    
    for msg in chat_hist[-min(len(chat_hist), n):]:
        curr_msgs.append(msg)    
    curr_msgs.append({"role": "user", "content": query})
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    # response_format={ "type": "json_object" },
    messages=curr_msgs
    )
    
    return response.choices[0].message.content


while True:
    
    query = input("prompt: ")
    router_answer = openAI_api_call("router", query)
    print("="*50)
    print(f"Router answer is:  {router_answer}")
    print("="*50)
    skip = False
    if "get_relevant_context" in router_answer:
        print("="*50)
        print(f"get_relevant_context")
        print("="*50)
    
        opt_query = openAI_api_call("text", query)
        print("="*50)
        print(f"opt_query {opt_query}")
        print("="*50)
    
        context = fetch_context(opt_query)
        print("="*50)
        print(f"context {context}")
        print("="*50)
        updated_query = update_query(opt_query, context)
        print("="*50)
        print(f"updated_query {updated_query}")
        print("="*50)
        answer = openAI_api_call("",updated_query)

        
        
        
        chat_hist.append({"role": "user", "content": query})
        chat_hist.append({"role": "assistant", "content": answer})
        print("@"*50)
        print(f"Answer: {answer}")
        print("@"*50)
        skip = True
    
    if "get_relevant_images" in router_answer:
        print("="*50)
        print(f"get_relevant_images")
        print("="*50)
        opt_query = openAI_api_call("images", query + ", " + answer)
        print("="*50)
        print(f"opt_query: {opt_query}")
        print("="*50)    
        images_urls = fetch_images(opt_query)
        print("@"*50)
        print(f"Found images: {images_urls}")
        print("@"*50)
        skip = True
    
    if (not skip):
        print("="*50)
        print(f"Answering from past")
        print("="*50)
        opt_query = openAI_api_call("text", query)
        print("="*50)
        print(f"opt_query: {opt_query}")
        print("="*50)
        answer = openAI_api_call("",opt_query)
        chat_hist.append({"role": "user", "content": query})
        chat_hist.append({"role": "assistant", "content": answer})
        print("@"*50)
        print(f"Answer: {answer}")
        print("@"*50)
    
    
    print("!"*50)
    print("ONE TURN FINISHED")
    print("!"*50)
    # break