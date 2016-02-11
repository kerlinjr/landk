# -*- coding: utf-8 -*-
chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# Set up window and text field
from psychopy import visual, event
win = visual.Window()
text = visual.TextStim(win, text='')

# Loop until return is pressed
endTrial = False

while not endTrial:
    # Wait for response...
    response = event.waitKeys()
    if response:
        print response
        # If backspace, delete last character
        if response[0] == 'backspace':
            text.setText(text.text[:-1])

        # If return, end trial
        elif response[0] == 'return':
            endTrial = True

        # Insert space
        elif response[0] == 'space':
            text.setText(text.text + ' ')

        # Else if a letter, append to text:
        elif response[0] in chars:
            text.setText(text.text + response[0])

    # Display updated text
    text.draw()
    win.flip()

# Print final response
print 'SUBJECT RESPONDED: ', text.text