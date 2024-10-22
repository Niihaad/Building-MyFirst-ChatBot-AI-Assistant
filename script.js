$(document).ready(function() {
    $("#sendButton").click(function() {
        let userInput = $("#messageInput").val();
        if (userInput.trim() === "") return;

        $("#chatlog").append(`<p class="user">Vous: ${userInput}</p>`);
        $("#messageInput").val("");

        $.post("/get_response", { msg: userInput })
    .done(function(data) {
        $("#chatlog").append(`<p class="bot">AI Assistant: ${data.response}</p>`);
        $("#chatlog").scrollTop($("#chatlog")[0].scrollHeight);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Erreur lors de l'appel AJAX:", textStatus, errorThrown);
        alert("Erreur : Impossible d'obtenir une réponse du serveur.");
    });

    });

    $("#messageInput").keypress(function(e) {
        if (e.which == 13) {
            $("#sendButton").click();
        }
    });
});
