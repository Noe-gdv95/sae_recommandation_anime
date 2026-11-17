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
async function chargerStats() {
    try {
        const stats = await api("/api/stats");
        $("stats").textContent = Object.entries(stats)
            .map(([k, v]) => `${fmtNombre(v)} ${LIBELLES_STATS[k] ?? k.replace(/^nb_|_count$/g, "")}`)
            .join(" · ");
    } catch {
        $("stats").textContent = "";
    }
}

async function chargerGenres() {
    try {
        const genres = liste(await api("/api/genres"), "genres");
        if (!genres.length) return;
        $("filtre-genre").append(...genres.map((g) => new Option(g.nom, g.id)));
        $("champ-genre").hidden = false;
    } catch {
        console.info("Route /api/genres absente.");
    }
}

// Catalogue & Recherche

async function chargerCatalogue() {
    const params = new URLSearchParams({ limit: 24 });
    const q = $("recherche").value.trim();
    if (q) params.set("q", q);
    if ($("filtre-genre").value) params.set("genre_id", $("filtre-genre").value);
    if ($("filtre-type").value) params.set("type_anime", $("filtre-type").value);

    setMessage("message", "Chargement…");
    try {
        const animes = liste(await api(`/api/animes?${params}`), "animes");
        $("grille").replaceChildren();

        if (!animes.length) {
            $("compteur").textContent = "";
            return setMessage("message", "Aucun anime ne correspond à ta recherche.");
        }

        setMessage("message", "");
        $("compteur").textContent = `${animes.length} anime${animes.length > 1 ? "s" : ""} affiché${animes.length > 1 ? "s" : ""}`;
        $("grille").append(...animes.map(creerCarte));
    } catch {
        $("grille").replaceChildren();
        $("compteur").textContent = "";
        setMessage("message", "Impossible de joindre l'API (port 8000).", true);
    }
}

function creerCarte(anime) {
    const carte = $("modele-carte").content.firstElementChild.cloneNode(true);
    carte.querySelector(".carte__type").textContent = NOMS_TYPES[anime.type] ?? anime.type ?? "Inconnu";
    carte.querySelector(".carte__note").textContent = fmtNote(anime.note_moyenne);

    const btn = carte.querySelector(".carte__titre button");
    btn.textContent = anime.nom;
    btn.onclick = () => ouvrirFiche(anime.id);

    const ep = anime.nb_episodes == null ? "? épisodes" : `${anime.nb_episodes} ép.`;
    carte.querySelector(".carte__details").textContent = `${ep} · ${fmtNombre(anime.nb_membres)} membres`;

    remplirGenres(carte.querySelector(".etiquettes"), anime.genres ?? [], 4);
    return carte;
}

//  Fiche & Recommandations


async function ouvrirFiche(id) {
    animeOuvert = id;
    $("fiche-titre").textContent = "Chargement…";
    ["fiche-type", "fiche-note", "fiche-episodes", "fiche-membres"].forEach((el) => $(el).textContent = "");
    $("fiche-genres").replaceChildren();
    $("fiche-recos").replaceChildren();
    setMessage("fiche-statut", "");

    if (!$("fiche").open) $("fiche").showModal();

    try {
        const anime = await api(`/api/animes/${id}`);
        $("fiche-type").textContent = NOMS_TYPES[anime.type] ?? anime.type ?? "Inconnu";
        $("fiche-titre").textContent = anime.nom;
        $("fiche-note").textContent = fmtNote(anime.note_moyenne);
        $("fiche-episodes").textContent = anime.nb_episodes ?? "Inconnu";
        $("fiche-membres").textContent = fmtNombre(anime.nb_membres);
        remplirGenres($("fiche-genres"), anime.genres ?? []);
        chargerRecommandations();
    } catch (err) {
        $("fiche-titre").textContent = err.status === 404 ? "Anime introuvable" : "Erreur de chargement";
    }
}

function creerOnglets() {
    $("fiche-methodes").replaceChildren(...METHODES.map((m) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "onglet";
        btn.textContent = m.libelle;
        btn.setAttribute("aria-pressed", m.id === methodeChoisie);
        btn.onclick = () => {
            methodeChoisie = m.id;
            [...$("fiche-methodes").children].forEach((b, i) =>
                b.setAttribute("aria-pressed", METHODES[i].id === methodeChoisie)
            );
            chargerRecommandations();
        };
        return btn;
    }));
}

async function chargerRecommandations() {
    const id = animeOuvert;
    $("fiche-recos").replaceChildren();
    setMessage("fiche-statut", "Calcul des recommandations…");

    try {
        const t0 = performance.now();
        const data = await api(`/api/animes/${id}/recommandations?methode=${methodeChoisie}&limit=10`);
        if (id !== animeOuvert) return;

        const recos = liste(data, "recommandations");
        if (!recos.length) return setMessage("fiche-statut", "Aucune recommandation trouvée.");

        setMessage("fiche-statut", `${recos.length} propositions (${Math.round(performance.now() - t0)} ms)`);
        $("fiche-recos").append(...recos.map(creerLigneReco));
    } catch (err) {
        if (id !== animeOuvert) return;
        const msg = err.status === 404 ? "Méthode indisponible." : "Erreur de calcul.";
        setMessage("fiche-statut", msg, err.status !== 404);
    }
}

function creerLigneReco(reco) {
    const anime = reco.anime ?? reco;
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "reco";
    btn.innerHTML = `<span>${anime.nom}</span>` +
        (reco.score != null ? `<span class="reco__score">similarité ${Math.round(reco.score * 100)} %</span>` : "");
    btn.onclick = () => ouvrirFiche(anime.id);
    li.append(btn);
    return li;
}

//  Mesures de performance

async function chargerMesures() {
    setMessage("message-mesures", "Chargement…");
    try {
        const [resume, dernieres] = await Promise.all([api("/api/mesures/resume"), api("/api/mesures")]);
        dessinerGraphique(resume);
        remplirTableauMesures(liste(dernieres, "mesures"));
        setMessage("message-mesures", "");
    } catch {
        setMessage("message-mesures", "Impossible de charger les mesures.", true);
    }
}

function dessinerGraphique(resume) {
    if (typeof Chart === "undefined") {
        return setMessage("message-mesures", "Chart.js non chargé.", true);
    }

    const keys = Object.keys(resume);
    const labels = keys.map((id) => METHODES.find((m) => m.id === id)?.libelle ?? id);
    const datasets = [
        { label: "Min (ms)", data: keys.map((k) => resume[k].temps_min_ms), backgroundColor: "#dce3ff" },
        { label: "Moyen (ms)", data: keys.map((k) => resume[k].temps_moyen_ms), backgroundColor: "#2b3cff" },
        { label: "Max (ms)", data: keys.map((k) => resume[k].temps_max_ms), backgroundColor: "#d6224f" },
    ];

    if (graphique) {
        Object.assign(graphique.data, { labels, datasets });
        return graphique.update();
    }

    graphique = new Chart($("graphique-mesures"), {
        type: "bar",
        data: { labels, datasets },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } },
    });
}

function remplirTableauMesures(mesures) {
    const tbody = $("corps-mesures");
    tbody.replaceChildren();

    if (!mesures.length) {
        tbody.insertRow().insertCell().textContent = "Aucune mesure : ouvre une fiche anime pour en créer.";
        tbody.rows[0].cells[0].colSpan = 5;
        return;
    }

    mesures.forEach((m) => {
        const tr = tbody.insertRow();
        [
            m.methode,
            m.anime_id,
            Number(m.temps_ms).toFixed(1).replace(".", ","),
            m.nb_resultats,
            m.date_mesure ? new Date(m.date_mesure).toLocaleString("fr-FR") : "—",
        ].forEach((val) => tr.insertCell().textContent = val ?? "—");
    });
}

// Événements & Démarrage

$("formulaire-recherche").onsubmit = (e) => {
    e.preventDefault();
    clearTimeout(minuteurRecherche);
    chargerCatalogue();
};
$("recherche").oninput = () => {
    clearTimeout(minuteurRecherche);
    minuteurRecherche = setTimeout(chargerCatalogue, 300);
};
$("filtre-genre").onchange = chargerCatalogue;
$("filtre-type").onchange = chargerCatalogue;

$("fiche-fermer").onclick = () => $("fiche").close();
$("fiche").onclick = (e) => { if (e.target === $("fiche")) $("fiche").close(); };
$("fiche").onclose = chargerMesures;
$("bouton-actualiser").onclick = chargerMesures;

creerOnglets();
chargerStats();
chargerGenres();
chargerCatalogue();
chargerMesures();




