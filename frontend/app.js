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


