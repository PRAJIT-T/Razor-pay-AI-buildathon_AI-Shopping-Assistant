const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");


function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `message ${type}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = type === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    // Detect payment URL
    const urlRegex = /https?:\/\/127\.0\.0\.1:8000\/pay\/ORD-[a-zA-Z0-9-]+/;

    const match = text.match(urlRegex);

    if (match) {
        const url = match[0];

        // Show everything before the URL
        const beforeUrl = text.substring(0, match.index);
        bubble.appendChild(document.createTextNode(beforeUrl));

        // Payment button
        const link = document.createElement("a");
        link.href = url;
        link.textContent = "💳 Pay with Razorpay";
        link.target = "_blank";

        link.style.display = "inline-block";
        link.style.marginTop = "10px";
        link.style.padding = "10px 16px";
        link.style.background = "#222";
        link.style.color = "white";
        link.style.borderRadius = "8px";
        link.style.textDecoration = "none";

        bubble.appendChild(link);

        // Anything after the URL
        const afterUrl = text.substring(match.index + url.length);
        if (afterUrl) {
            bubble.appendChild(document.createTextNode(afterUrl));
        }
    } else {
        bubble.textContent = text;
    }

    message.appendChild(avatar);
    message.appendChild(bubble);

    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;
}


async function sendMessage() {

    const message = input.value.trim();

    if (!message) {
        return;
    }


    // Show user's message
    addMessage(message, "user");


    // Clear input
    input.value = "";


    // Disable while AI is responding
    sendButton.disabled = true;
    input.disabled = true;


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(data.detail || "Request failed");
        }


        // Show AI response
        addMessage(data.response, "ai");


    } catch (error) {

        addMessage(
            "Sorry, something went wrong: " + error.message,
            "ai"
        );

    } finally {

        sendButton.disabled = false;
        input.disabled = false;

        input.focus();
    }
}


sendButton.addEventListener("click", sendMessage);


input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});

// Handle successful payment return from Razorpay
// Receive verified payment confirmation from the Razorpay payment tab
window.addEventListener("message", function (event) {

    if (event.origin !== "http://127.0.0.1:8000") {
        return;
    }

    if (!event.data || event.data.type !== "PAYMENT_SUCCESS") {
        return;
    }

    const orderId = event.data.orderId;

    addMessage(
        `🎉 Payment successful!\n\n` +
        `Your order ${orderId} has been paid and confirmed.\n\n` +
        `Thank you for your purchase!`,
        "ai"
    );
});