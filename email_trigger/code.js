// This function will run automatically every time a form is submitted.
function sendResultsLink(e) {
  
  // --- CONFIGURATION ---
  // IMPORTANT: Replace this with the URL of your deployed Streamlit app
  const STREAMLIT_APP_URL = "https://woynhpxcdqkfmf5khvnjvv.streamlit.app"; 
  // --------------------

  try {
    // Get the email address from the form submission.
    // Make sure your Google Form question for the email is titled "Work Email Address".
    var email = e.namedValues['Work Email Address'][0];
    
    // Get the user's name to personalize the email, if you have a "Name" column.
    var name = e.namedValues['Name'] ? e.namedValues['Name'][0] : '';
    var greeting = name ? `Hi ${name},` : 'Hi,';

    // URL-encode the email to handle special characters like '+'
    var encodedEmail = encodeURIComponent(email);
    
    // Construct the personalized URL
    var resultsUrl = `${STREAMLIT_APP_URL}/?email=${encodedEmail}`;
    
    // Define the email subject and body
    var subject = "Your Strategic Impact Profile is Ready";
    var body = `
      <p>${greeting}</p>
      <p>Thank you for completing the Strategic Impact Self-Assessment.</p>
      <p>You can view your personalized dashboard by clicking the link below:</p>
      <p><a href="${resultsUrl}" style="font-size: 16px; font-weight: bold; color: #FFFFFF; background-color: #0068C9; text-decoration: none; padding: 10px 20px; border-radius: 5px;">View My Profile</a></p>
      <p>This link is personalized for you. Please do not share it.</p>
    `;
    
    // Send the email
    MailApp.sendEmail({
      to: email,
      subject: subject,
      htmlBody: body // Use htmlBody to make the link clickable
    });
    
    Logger.log(`Successfully sent results link to ${email}`);
    
  } catch (error) {
    // Log any errors for debugging
    Logger.log(`Error sending email: ${error.toString()}`);
  }
}