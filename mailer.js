/**
 * Nodemailer Email Dispatcher for SkillHer Contact Form
 * Invoked by Django backend to handle transactional emails
 */
const nodemailer = require('nodemailer');

async function main() {
    let inputData = '';
    
    // Read from CLI argument or standard input
    if (process.argv[2]) {
        inputData = process.argv[2];
    } else {
        inputData = await new Promise((resolve) => {
            let data = '';
            process.stdin.on('data', chunk => data += chunk);
            process.stdin.on('end', () => resolve(data));
        });
    }

    if (!inputData) {
        console.error(JSON.stringify({ status: 'error', message: 'No input payload provided' }));
        process.exit(1);
    }

    let payload;
    try {
        payload = JSON.parse(inputData);
    } catch (e) {
        console.error(JSON.stringify({ status: 'error', message: 'Invalid JSON payload: ' + e.message }));
        process.exit(1);
    }

    const { name, email, subject, category, message } = payload;

    // Configure transporter
    let transporter;
    const smtpHost = process.env.SMTP_HOST;
    const smtpUser = process.env.SMTP_USER;
    const smtpPass = process.env.SMTP_PASS;

    if (smtpHost && smtpUser && smtpPass) {
        transporter = nodemailer.createTransport({
            host: smtpHost,
            port: parseInt(process.env.SMTP_PORT || '587', 10),
            secure: process.env.SMTP_SECURE === 'true',
            auth: {
                user: smtpUser,
                pass: smtpPass
            }
        });
    } else {
        // Safe development JSON transport: builds full email object & generates messageId without external network failure
        transporter = nodemailer.createTransport({
            jsonTransport: true
        });
    }

    const mailOptions = {
        from: `"${name}" <${email}>`,
        to: process.env.CONTACT_EMAIL || 'malthumkarvarun@gmail.com',
        replyTo: email,

        subject: `[SkillHer Contact - ${category || 'General'}] ${subject}`,
        text: `From: ${name} (${email})\nCategory: ${category}\n\nMessage:\n${message}`,
        html: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h2 style="color: #6366f1; border-bottom: 2px solid #8b5cf6; padding-bottom: 10px;">New SkillHer Contact Inquiry</h2>
                <p><strong>Sender Name:</strong> ${name}</p>
                <p><strong>Email Address:</strong> <a href="mailto:${email}">${email}</a></p>
                <p><strong>Category:</strong> ${category || 'General Inquiry'}</p>
                <p><strong>Subject:</strong> ${subject}</p>
                <div style="margin-top: 20px; padding: 15px; background-color: #f8fafc; border-left: 4px solid #6366f1; border-radius: 4px;">
                    <h4 style="margin-top: 0; color: #1e293b;">Message:</h4>
                    <p style="white-space: pre-wrap; color: #334155; margin-bottom: 0;">${message}</p>
                </div>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 25px 0 15px;" />
                <p style="font-size: 12px; color: #94a3b8;">Sent via SkillHer Platform &bull; Powered by Nodemailer</p>
            </div>
        `
    };

    try {
        const info = await transporter.sendMail(mailOptions);
        console.log(JSON.stringify({
            status: 'success',
            messageId: info.messageId,
            to: mailOptions.to,
            subject: mailOptions.subject,
            preview: info.message ? 'Simulated via Nodemailer JSON transport' : 'Sent via SMTP'
        }));
    } catch (err) {
        console.error(JSON.stringify({
            status: 'error',
            message: err.message
        }));
        process.exit(1);
    }
}

main().catch(err => {
    console.error(JSON.stringify({ status: 'error', message: err.message }));
    process.exit(1);
});
