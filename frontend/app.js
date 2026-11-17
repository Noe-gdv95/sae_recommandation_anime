const API_URL = "http://localhost:8000";
const METHODES = [
    { id: "contenu", libelle: "Par genres" },
    { id: "collaboratif", libelle: "Par spectateurs" },
];
const NOMS_TYPES = {
    TV: "Série TV", Movie: "Film", OVA: "OVA",
    ONA: "ONA", Special: "Spécial", Music: "Clip musical",
};
const LIBELLES_STATS = {
    animes_count: "anime", nb_animes: "anime",
    genres_count: "genres", nb_genres: "genres",
    ratings_count: "notes", notes_count: "notes", nb_notes: "notes", nb_ratings: "notes",
    users_count: "spectateurs", nb_utilisateurs: "spectateurs",
};

const $ = (id) => document.getElementById(id);

let animeOuvert = null;
let methodeChoisie = METHODES[0].id;
let graphique = null;
let minuteurRecherche = null;


// Outils
async function api(chemin) {
    const res = await fetch(API_URL + chemin);
    if (!res.ok) throw Object.assign(new Error(`Erreur ${res.status}`), { status: res.status });
    return res.json();
}

const liste = (data, cle) => Array.isArray(data) ? data : (data?.[cle] ?? data?.resultats ?? []);
const fmtNombre = (n) => n == null ? "—" : Number(n).toLocaleString("fr-FR");
const fmtNote = (n) => n == null ? "—" : Number(n).toFixed(2).replace(".", ",");

function setMessage(id, texte, estErreur = false) {
    const el = $(id);
    el.textContent = texte;
    el.classList.toggle("message--erreur", estErreur);
}

function remplirGenres(ul, genres, max = Infinity) {
    ul.replaceChildren(...genres.slice(0, max).map((g) => {
        const li = document.createElement("li");
        li.className = "etiquette";
        li.textContent = g;
        return li;
    }));
}

// Statistiques & Genres

