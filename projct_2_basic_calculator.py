import tkinter as tk
from tkinter import messagebox
import math
import speech_recognition as sr
import pyttsx3
import threading
import re
import sympy as sp

class VoiceInterface:
    def __init__(self):                       #initializing the speech recognizer and text-to-speech engine 
        self.recognizer = sr.Recognizer()     #initializing the speech recognizer from the speech_recognition library to handle voice input recognition                                  
        self.engine = pyttsx3.init()        #initializing the pyttsx3 engine for text-to-speech
        self.engine.setProperty('rate', 150)    #setting the speech rate of the engine to 150 words per minute
        voices = self.engine.getProperty('voices')  #retrieving the available voices from the text-to-speech engine
        if voices:                              #checking if there are any voices available
            self.engine.setProperty('voice', voices[1].id)  #setting the voice of the engine to the first available voice if there are any voices available
    
    def listen(self, prompt=None):                                   #listening for voice input using the microphone and returning the recognized text
        if prompt:
            self.speak(prompt)
        with sr.Microphone() as source:                                         #using the microphone as the audio source for listening
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)      #adjusting the recognizer to account for ambient noise for better recognition accuracy
            try:                                                                #listening for audio input with a timeout of 5 seconds to prevent indefinite waiting
                audio = self.recognizer.listen(source, timeout=5)               #capturing the audio input from the microphone
                text = self.recognizer.recognize_google(audio)  
                                    #using Google's speech recognition to convert the audio input into text and returning it
                return text
            except Exception:                                                   #handling any exceptions that occur during listening or recognition and returning None if an error occurs
                return None                                                     #returning None if an error occurs during listening or recognition

    def speak(self, text):                                                      #speaking the given text using the text-to-speech engine, this method is designed to be run in a separate thread to avoid freezing the GUI while speaking
        
        self.engine.say(text)                                       #queuing the text to be spoken by the engine        
        self.engine.runAndWait()                    #running the engine to process the queued text and produce speech output    

class ScientificCalculator:                                                     #main class for the scientific calculator application, responsible for creating the GUI, handling user interactions, and performing calculations
    def __init__(self, root):                                                   #initializing the calculator application with the given root window, setting up the GUI components, and initializing necessary variables and the voice interface
        self.root = root                                                        #setting the title of the root window to "Calculus & Scientific Calculator"
        self.root.title("Calculus & Scientific Calculator")                     #setting the size of the root window to 450x750 pixels
        self.root.geometry("450x750")                               #configuring the background color of the root window to black   
        self.root.configure(bg="black")                                 

        self.expression = ""                                               #initializing an empty string to hold the current mathematical expression being entered by the user  
        self.voice = VoiceInterface()                                       #creating an instance of the VoiceInterface class to handle voice input and output  
        self.listening = False                                                   #initializing a flag to indicate whether the application is currently listening for voice input
                                                            #creating an entry widget to serve as the display screen for the calculator, with specific font, background color, foreground color, and text alignment properties
        self.display = tk.Entry(root, font=("Arial", 22), bd=10, insertwidth=4, 
                                bg="#222", fg="white", justify="right")
        self.display.pack(fill="both", ipadx=8, ipady=20, padx=10, pady=10)

       
        tk.Label(root, text="Use 'x' as variable for Calculus",             #adding a label to the root window to provide instructions for using 'x' as the variable for calculus operations, with specific font and color properties
                 fg="#888", bg="black", font=("Arial", 9)).pack()

        # Voice Button
        self.voice_btn = tk.Button(root, text=" Click and Speak", font=("Arial", 12, "bold"),       #creating a button for voice input with specific text, font, background color, foreground color, and command to execute when clicked
                                   bg="#4CAF50", fg="white", command=self.toggle_voice_input)
        self.voice_btn.pack(fill="x", padx=10, pady=5)
        self.status_label = tk.Label(root, text="", fg="#888", bg="black", font=("Arial", 9))
        self.status_label.pack()

        self.create_buttons()                                                                   #calling the method to create the calculator buttons and arrange them in the GUI

        #threading.Thread(target=lambda: self.voice.speak("Welcome to Next Hikes Calculator"), daemon=True).start()
    def create_buttons(self):                                #method to create the calculator buttons and arrange them in a grid layout, with specified text, position, and command to execute when clicked     
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(expand=True, fill="both")

        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3), ("C", 1, 4),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3), ("√", 2, 4),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3), ("x²", 3, 4),
            ("0", 4, 0), (".", 4, 1), ("x", 4, 2), ("+", 4, 3), ("=", 4, 4),
            ("sin", 5, 0), ("cos", 5, 1), ("tan", 5, 2), ("log", 5, 3), ("**", 5, 4),
            ("d/dx", 6, 0), ("∫", 6, 1), ("(", 6, 2), (")", 6, 3), ("π", 6, 4)
        ]

        for text, row, col in buttons:                                              #iterating through the list of button specifications to create and place each button in the grid layout, with specific text, position, background color, and command to execute when clicked
            bg_color = "#333333"
            if text in ["d/dx", "∫"]: bg_color = "#FF9500"
            elif text == "=": bg_color = "#4CAF50"
            elif text == "C": bg_color = "#F44336"

            btn = tk.Button(btn_frame, text=text, width=6, height=2, font=("Arial", 12, "bold"),        #creating a button with the specified text, size, font, background color, foreground color, and command to execute when clicked
                            bg=bg_color, fg="white", relief="flat",
                            command=lambda t=text: self.on_click(t))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        for i in range(5):                                                        #configuring the grid layout to allow the buttons to expand and fill the available space evenly   
            btn_frame.grid_columnconfigure(i, weight=1)                            

    def on_click(self, value):                                              #method to handle button clicks, updating the current expression based on the button clicked and performing calculations or updates to the display as needed
        if value == "C":
            self.expression = ""
        elif value == "=":
            self.calculate_standard()
        elif value == "d/dx":
            self.calculate_calculus("diff")
        elif value == "∫":
            self.calculate_calculus("integrate")
        elif value == "x²":
            self.expression += "**2"
        elif value == "√":
            self.expression += "math.sqrt("
        elif value == "π":
            self.expression += "3.14159265"
        elif value in ["sin", "cos", "tan"]:
            self.expression += f"math.{value}("
        else:
            self.expression += str(value)
        self.update_display()
    
    def add_auto_close_parens(self):                                            
        """Automatically adds closing parenthesis for functions"""
        open_count = self.expression.count('(') - self.expression.count(')')        
        return ')' * open_count

    def update_display(self):                                                   #method to update the calculator display with the current expression, clearing the display and inserting the updated expression for the user to see
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

    def calculate_standard(self):                                           #method to evaluate the current expression using Python's eval function, with error handling to catch invalid expressions and display an error message if the evaluation fails
        try:
           # Auto-close any open parentheses
           expr = self.expression + self.add_auto_close_parens()
           expr = self._normalize_for_eval(expr)                            #normalizing the expression to ensure it is in a format that can be evaluated correctly, such as handling function names and operators appropriately
           result = eval(expr)
           self.expression = str(round(result, 8))                          #rounding the result to 8 decimal places and converting it to a string to update the expression with the calculated result
           self.update_display()
        except Exception as e:                                              #handling any exceptions that occur during evaluation and displaying an error message to the user if the expression is invalid, then clearing the expression to allow for a new calculation
            messagebox.showerror("Error", "Invalid Expression")
            self.clear()
            

    def _normalize_for_eval(self, expr):                                         #method to normalize the expression for evaluation, such as replacing certain symbols with their corresponding Python functions or operators, and ensuring that the expression is in a format that can be evaluated correctly
        s = re.sub(r"\s+", "", expr)
        # Wrap trig functions to handle degrees automatically
        def _wrap_trig(match):                                                  #helper function to wrap trigonometric functions (sin, cos, tan) to automatically convert degrees to radians for evaluation, using a regular expression to match the function and its argument and returning the modified expression with the appropriate math function and conversion
            fn, arg = match.group(1), match.group(2).strip("()")
            return f"math.{fn}(math.radians({arg}))"
        # Match "math.sin(30)" format - handle the "math." prefix properly
        s = re.sub(r"math\.(sin|cos|tan)\(([^)]+)\)", _wrap_trig, s)
        return s

    def calculate_calculus(self, func):                                         #method to calculate derivatives and integrals using the sympy library, taking the current expression, converting it to a sympy expression, and performing the requested calculus operation (differentiation or integration) while handling any exceptions that may occur during the process and displaying appropriate messages to the user
        """Calculate derivatives and integrals using sympy"""
        if not self.expression:                                                 #if the expression is empty, show a warning message to the user and return without performing any calculations, as calculus operations require an expression to work with
            messagebox.showwarning("Warning", "Please enter an expression with variable 'x'")
            return
        try:                                                                    #defining the variable 'x' for sympy to use in calculus operations, and converting the current expression into a format suitable for sympy to process, such as replacing certain symbols and ensuring that the expression is in a format that can be parsed by sympy
            x = sp.Symbol('x')
            expr_str = self.expression.replace('π', 'pi').replace('math.', '')
            expr = sp.sympify(expr_str)
            
            if func == "diff":
                result = sp.diff(expr, x)
                self.expression = str(result)
            elif func == "integrate":
                result = sp.integrate(expr, x)
                self.expression = str(result) + " + C"
            
            self.update_display()
            messagebox.showinfo("Result", f"Result: {self.expression}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot perform calculus operation:\n{str(e)}")
            
    
    def _normalize_for_sympy(self, expr):
        s = expr.replace('^', '**').replace('math.sqrt', 'sqrt').replace('π', 'pi')
        s = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', s) # 2x -> 2*x
        return s

    def clear(self):                                                            #method to clear the current expression and update the display, resetting the calculator to its initial state for a new calculation
        self.expression = ""
        self.update_display()

    def toggle_voice_input(self):                                               #method to toggle the voice input mode, starting a new thread to listen for voice commands when activated, and updating the button text and color to indicate that the application is listening for voice input
        if not self.listening:
            self.listening = True
            self.voice_btn.config(text="Listening...", bg="#F44336")
            threading.Thread(target=self.process_voice_command, daemon=True).start()
    
    def process_voice_command(self):                                            #method to process the voice command received from the user, parsing the command to extract the mathematical expression, performing any necessary normalization or conversion, and then evaluating the expression or performing calculus operations as needed, while also providing feedback to the user through voice output and updating the display accordingly
        cmd = self.voice.listen()
        if cmd:
            self.parse_voice_command(cmd)
        else:   
            self.voice.speak("Sorry, I didn't catch that.")

        
        self.root.after(0, lambda: self.voice_btn.config(text="🎤 Click to Speak", bg="#4CAF50"))
        self.listening = False
    
    def parse_voice_command(self, cmd):                                         
        """Parse voice commands with expanded vocabulary"""
        cmd = cmd.lower().strip()                                           #converting the received voice command to lowercase and stripping any leading or trailing whitespace to standardize the input for further processing
        
        replacements = {
            "plus": "+", "add": "+",
            "minus": "-", "subtract": "-",
            "times": "*", "multiply": "*", "multiplied by": "*",
            "divided by": "/", "divide": "/", "over": "/",
            "equals": "=", "equal": "=", "is equal to": "=",
            "clear": "C", "reset": "C", "delete": "C",
            "open paren": "(", "open parenthesis": "(", "open bracket": "(",
            "close paren": ")", "close parenthesis": ")", "close bracket": ")",
            "derivative of": "d/dx", "differentiate": "d/dx", "derivative": "d/dx",
            "integral of": "∫", "integrate": "∫", "integral": "∫",
            "sine": "sin", "sin": "sin",
            "cosine": "cos", "cos": "cos",
            "tangent": "tan", "tan": "tan",
            "pi": "π", "pie": "π",
            "squared": "**2", "square": "**2", "power of 2": "**2",
            "cubed": "**3", "power of 3": "**3", "cube": "**3",
            "square root": "√", "root": "√",
            "log": "log(", "logarithm": "log(",
            "power": "**", "to the power": "**", "raised to": "**",
            "point": ".", "decimal": ".",
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        }
        
        for word, symbol in replacements.items():                                               #iterating through the replacements dictionary to replace any occurrences of the specified words in the command with their corresponding symbols, allowing for a more natural language input for mathematical expressions
            cmd = cmd.replace(word, symbol)
        
        # FIXED: Allow function names (sin, cos, tan, log), math operators, and special symbols
        clean_expr = "".join([c for c in cmd if c in "0123456789+-*/=().xsincotan lgπ√"])
        
        if clean_expr.strip():                                                      #if the cleaned expression is not empty after removing any unwanted characters, update the current expression with the cleaned version and proceed to evaluate it or perform calculus operations as needed, while also providing feedback to the user through voice output and updating the display accordingly
            self.expression = clean_expr.strip()
            
            if "d/dx" in self.expression:
                self.expression = self.expression.replace("d/dx", "").strip()
                self.calculate_calculus("diff")
                return
            elif "∫" in self.expression:
                self.expression = self.expression.replace("∫", "").strip()
                self.calculate_calculus("integrate")
                return
            
            self.update_display()                                                   #updating the calculator display with the cleaned expression for the user to see, and then checking if the expression contains an equals sign to determine if it should be evaluated as a standard expression or if it should simply be spoken back to the user, providing feedback through voice output accordingly
            if "=" in self.expression:
                self.expression = self.expression.replace("=", "").strip()
                self.calculate_standard()
                self.voice.speak(f"The result is {self.expression}")
            else:
                self.voice.speak(f"Expression is {self.expression}")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()