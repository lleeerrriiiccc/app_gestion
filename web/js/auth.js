export async function getUser() {
    const res = await fetch("/api/me", {
        method: "GET",
        credentials: "include"   // ← OBLIGATORIO para enviar cookies
    });

    const data = await res.json();
    if (res.ok) {
        return data;
    } else {
        throw new Error(data.message || "No se pudo obtener la información del usuario.");
    }
}

