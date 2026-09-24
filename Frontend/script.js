document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("query");
    const button = document.getElementById("sendBtn");
    const chatWindow = document.getElementById("chat-window");
  
    function addMessage(text, sender) {
        const message = document.createElement("div");
        message.className = `message ${sender}`;
        const content = document.createElement("div");
        content.className = "message-content";
        content.innerHTML = text;
        message.appendChild(content);
        chatWindow.appendChild(message);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return content;
    }

    function formatAIResponse(text) {
        text = text
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .replace(/[ \t]+\n/g, "\n")
            .replace(/\n[ \t]+/g, "\n")
            .replace(/\n{3,}/g, "\n\n")
            .trim();

        text = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        text = text.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );

        text = text.replace(
            /^#{1,6}\s*(.+)$/gm,
            '<div class="ai-heading">$1</div>'
        );

        text = text.replace(
            /^(✈️ Flights|🏨 Hotels|🍛 Food|🗺️ Places|💰 Budget|📅 Itinerary|💰 TOTAL SPEND|⭐ Recommendations)$/gm,
            '<div class="ai-heading">$1</div>'
        );

        text = text.replace(
            /^(Day\s+\d+:[^\n]+)$/gm,
            '<div class="day-heading">$1</div>'
        );

        text = text.replace(
            /^([a-z])\.\s+(.+)$/gim,
            '<div class="ai-point"><span class="point-label">$1.</span><span>$2</span></div>'
        );

        text = text.replace(
            /^(\d+)\.\s+(.+)$/gm,
            '<div class="ai-point"><span class="point-label">$1.</span><span>$2</span></div>'
        );

        text = text.replace(
            /^[*-]\s+(.+)$/gm,
            '<div class="ai-point"><span class="bullet">•</span><span>$1</span></div>'
        );

        text = text.replace(
            /\n/g,
            "<br>"
        );

        text = text.replace(
            /<br>\s*(<div class="ai-heading">)/g,
            "$1"
        );

        text = text.replace(
            /(<\/div>)\s*<br>/g,
            "$1"
        );

        text = text.replace(
            /<br>\s*(<div class="day-heading">)/g,
            "$1"
        );
        return text;
    }

    async function sendMessage() {
        const query = input.value.trim();
        if (!query) {
            return;
        }
        addMessage(
            escapeHTML(query),
            "user"
        );
        input.value = "";
        button.disabled = true;
        const aiMessage = addMessage(
            "",
            "ai"
        );
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: query
                    })
                }
            );

            if (!response.ok) {
                throw new Error(
                    `HTTP error: ${response.status}`
                );
            }

            if (!response.body) {
                throw new Error(
                    "Streaming is not supported by this browser."
                );
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let fullText = "";

            while (true) {
                const {
                    done,
                    value
                } = await reader.read();

                if (done) break;
                const text =
                    decoder.decode(
                        value,
                        {
                            stream: true
                        }
                    );

                fullText += text;

                aiMessage.innerHTML =formatAIResponse(fullText);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
            fullText += decoder.decode();
            aiMessage.innerHTML =formatAIResponse(fullText);

        } catch (error) {
            console.error(error);
            aiMessage.innerHTML ="⚠️ Error connecting to the server.";
        } finally {
            button.disabled = false;
            input.focus();
        }
    }

    function escapeHTML(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    button.addEventListener(
        "click",
        sendMessage
    );
    input.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Enter" && !event.shiftKey) 
            {
                event.preventDefault();
                sendMessage();
            }
        }
    );
});