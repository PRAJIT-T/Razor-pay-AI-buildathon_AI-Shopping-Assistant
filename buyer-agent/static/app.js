const chat = document.getElementById("chat");
const input = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");


function addMessage(text, type , showPayButton= true) {
    const message = document.createElement("div");
    message.className = `message ${type}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = type === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    // Find the real Order ID
    const orderMatch = text.match(/\bORD-[a-zA-Z0-9-]+\b/);
    const isPaymentPrompt = /pay|checkout|complete.*payment/i.test(text) && !/error|failed|cancel|audit/i.test(text);

    if (orderMatch && showPayButton && isPaymentPrompt) {
        const orderId = orderMatch[0];

        // Remove placeholder if AI used one
        let displayText = text.replace(
            /\[[^\]]*\]\([^)]*\)/g,
            ""
        ).trim();

        bubble.appendChild(
            document.createTextNode(displayText)
        );

        // Payment button
        const link = document.createElement("a");

        link.href = "#";
        link.textContent = "💳 Pay with Razorpay";

        link.style.display = "inline-block";
        link.style.marginTop = "10px";
        link.style.padding = "10px 16px";
        link.style.background = "#222";
        link.style.color = "white";
        link.style.borderRadius = "8px";
        link.style.textDecoration = "none";

        link.onclick = function(event) {
            event.preventDefault();

            const paymentUrl =
                "http://127.0.0.1:8000/pay/" + orderId;

            window.open(
                paymentUrl,
                "razorpay_payment",
                "width=500,height=750"
            );
        };

        bubble.appendChild(link);

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

// Receive verified payment confirmation
// from the Razorpay payment window

window.addEventListener("message", function(event) {

    if (!event.data || (event.data.type !== "PAYMENT_SUCCESS" && event.data.type !== "PAYMENT_FAILED")) {
        return;
    }

    if (!event.data) {
        return;
    }

    if (event.data.type === "PAYMENT_SUCCESS") {

        const orderId = event.data.orderId;

        addMessage(
            `-----Payment successful!-----\n\n` +
            `Your order ${orderId} has been paid and confirmed.\n\n` +
            `Thankyou for purchasing!`,
            "ai",
            false
        );
        const invoiceLink = document.createElement("a");
        invoiceLink.href = `http://127.0.0.1:8000/orders/${orderId}/invoice`;
        invoiceLink.target = "_blank";
        invoiceLink.textContent = "Download invoice";
        invoiceLink.style.display = "inline-block";
        invoiceLink.style.marginTop = "8px";
        invoiceLink.style.color = "#222";
        chat.lastElementChild.querySelector(".bubble").appendChild(document.createElement("br"));
        chat.lastElementChild.querySelector(".bubble").appendChild(invoiceLink);
    }
    if (event.data.type === "PAYMENT_FAILED") {
        addMessage(
            `Payment failed: ${event.data.reason}\n\nThe order is still pending — you can try paying again.`,
            "ai",
            false
        );
    }

});