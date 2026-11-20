import sys
import time
import traceback
import config
import pipeline

def start_chat():
    print("[-] Script launched. Initializing...") 
    config.setup_logging()
    
    try:
        print("[-] Starting Pipeline Build...")
        start_time = time.time()
        
        engine, guard = pipeline.build_rag_pipeline()
        
        elapsed = time.time() - start_time
        print(f"[-] Secure Pipeline Ready! (Time: {elapsed:.2f}s)")
        
        print("\n" + "="*60)
        print("TML Secure Bot (Llama Guard Taxonomy Implemented)")
        print("="*60 + "\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Bot: Goodbye!")
                break
            
            is_safe, reason = guard.check(user_input)
            
            if not is_safe:
                print(f"{reason}\n")
                continue

            response = engine.query(user_input)
            
            print(f"Bot: {response}\n")

    except Exception:
        print("\n[!] CRITICAL ERROR DETECTED")
        traceback.print_exc()

if __name__ == "__main__":
    start_chat()