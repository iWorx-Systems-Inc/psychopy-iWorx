from psychopy.experiment.components import BaseComponent, Param
from psychopy.constants import (NOT_STARTED, STARTED, FINISHED)
from pathlib import Path

# Path for the icon shown in the Builder toolbar
# Get the directory where THIS __init__.py is located
thisFolder = Path(__file__).parent.absolute()

# Define the icon file path
iconFile = str(thisFolder / 'MessageLabScribe.png')

class MessageLabScribeComponent(BaseComponent):
    """
    A Builder component to send TCP strings to LabScribe (iWorx) software.
    """
    categories = ['Hardware']
    targets = ['PsychoPy', 'PyGame', 'Pyglet']
    
    def __init__(self, exp, parentName, name='labScribe', 
                 address='127.0.0.1', port=3000, message='TRIGGER_1', 
                 startEstim=0.0):
        super(MessageLabScribeComponent, self).__init__(
            exp, parentName, name, startEstim=startEstim)
        
        self.type = 'MessageLabScribe'
        self.iconFile = iconFile  # Explicitly link the icon to the class
        self.url = "https://iworx.com/support/labscribe-manual/"

        # --- Parameters for the Builder Dialog Box ---
        self.params['address'] = Param(
            val=address, valType='str', allowedTypes=[],
            updates='constant',
            hint="IP of the LabScribe computer (127.0.0.1 if local)",
            label="IP Address")
            
        self.params['port'] = Param(
            val=port, valType='num', allowedTypes=[],
            updates='constant',
            hint="TCP Port (usually 3000 for LabScribe)",
            label="Port")
            
        self.params['message'] = Param(
            val=message, valType='str', allowedTypes=[],
            updates='each repeat',  # Allows using variables from Excel
            hint="The string/message to send (e.g., 'A')",
            label="TCP Message")

    def writeInitCode(self, buff):
        """Initializes the socket once at the very start of the experiment."""
        buff.writeIndented("import socket\n")
        buff.writeIndented(f"try:\n")
        buff.setIndentLevel(1, relative=True)
        buff.writeIndented(f"{self.name}_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n")
        buff.writeIndented(f"{self.name}_sock.settimeout(0.5)\n")
        buff.writeIndented(f"{self.name}_sock.connect(({self.params['address']}, {self.params['port']}))\n")
        buff.writeIndented(f"{self.name}_connected = True\n")
        buff.setIndentLevel(-1, relative=True)
        buff.writeIndented("except Exception as e:\n")
        buff.setIndentLevel(1, relative=True)
        buff.writeIndented(f"print(f'LabScribe Connection Error on {self.name}: {{e}}')\n")
        buff.writeIndented(f"{self.name}_connected = False\n")
        buff.setIndentLevel(-1, relative=True)

    def writeRoutineStartCode(self, buff):
        """Reset the 'sent' status so it triggers once per routine."""
        buff.writeIndented(f"{self.name}_sent = False\n")

    def writeFrameCode(self, buff):
        """Checks timing every frame to send the TCP message at the offset."""
        # startTime is the value entered in the 'Start' field in Builder
        startTime = self.params['startEstim']
        
        # Determine if we use a variable or a hardcoded number for the message
        msg = self.params['message']
        
        buff.writeIndented(f"if t >= {startTime} and not {self.name}_sent:\n")
        buff.setIndentLevel(1, relative=True)
        buff.writeIndented(f"if {self.name}_connected:\n")
        buff.setIndentLevel(1, relative=True)
        
        # Schedule the send for the next visual flip to maintain sync with stimulus
        buff.writeIndented(f"win.callOnFlip({self.name}_sock.sendall, str({msg}).encode('utf-8'))\n")
        buff.writeIndented(f"{self.name}_sent = True\n")
        
        buff.setIndentLevel(-2, relative=True)

    def writeExperimentEndCode(self, buff):
        """Close the TCP connection gracefully when experiment ends."""
        buff.writeIndented(f"if {self.name}_connected:\n")
        buff.setIndentLevel(1, relative=True)
        buff.writeIndented(f"{self.name}_sock.close()\n")
        buff.setIndentLevel(-1, relative=True)