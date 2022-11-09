To run the app:
1. in a command prompt, navigate to the directory containing the steamapp folder
2. run the command: flask --app steamapp --debug run
3. navigate to http://127.0.0.1:5000 OR open templates/home.html in your web browser
4. type a review and submit it
For now, it returns a results page with some dummy review scores

Next steps:
Add logic for processing reviews and getting model outputs
Send model outputs to results page template
Beautify template for results page