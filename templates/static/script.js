document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const usuario = document.getElementById("usuario").value;
    const senha = document.getElementById("senha").value;
    const mensagem = document.querySelector(".mensagem");

    // Simulação de login simples (pode integrar com backend depois)
    if (usuario === "admin" && senha === "1234") {
        mensagem.style.color = "lime";
        mensagem.textContent = "Login bem-sucedido! Redirecionando...";
        setTimeout(() => {
            window.location.href = "home.html"; // futura página principal
        }, 1500);
    } else {
        mensagem.style.color = "red";
        mensagem.textContent = "Usuário ou senha incorretos!";
    }
});
