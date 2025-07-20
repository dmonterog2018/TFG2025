const COMMITS_PER_ROW = 6;

/* Ruta al JSON con los datos */
const DATA_URL = '../commits_with_contents.json';


const el = (tag, cls = '', txt = '') => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (txt) n.textContent = txt;
  return n;
};

/* LECTURA DE DATOS */
fetch(DATA_URL)
  .then(r => r.json())
  .then(commits => {
     console.log(commits[0]);

    const repoName = commits.length > 0 ? commits[0].Repository : "Repositorio desconocido"; /* SI NO CONSEGUIMOS EL NOMBRE DEL REPO, PONEMOS DESCONOCIDO */
    document.getElementById("repoName").textContent = repoName;

    const timeline = document.getElementById('timeline');

    /* NODO INICIO */
    const startNode = el('div', 'commit-node top start-node');
    const startCircle = el('div', 'commit-circle', 'INICIO');

    const firstCommit = commits[0];
    const startTip = el('div', 'tooltip small-tooltip');
    startTip.innerHTML = `
      <strong>${new Date(firstCommit.date).toLocaleDateString()}</strong>
    `;

    startNode.appendChild(startCircle);
    startNode.appendChild(startTip);
    timeline.appendChild(startNode);

    /* NODO POR COMMIT */
    commits.forEach((c, i) => {

      const pos = i % 2 === 0 ? 'top' : 'bottom';
      const colorClass = 'color-' + ((i % 7) + 1);
      const node = el('div', `commit-node ${pos} ${colorClass}`);

      /* SACAMOS EL AUTOR DEL COMMIT SOLO EL NOMBRE CORREO NO NOS INTERESA */
      const authorFull = c.author || 'Desconocido';
      const authorName = authorFull.split(' <')[0];

      /* LINK A INDEX.HTML POR COMMIT PARA PODER COMPARAR */
      const link = document.createElement('a');
      link.href = `index.html?commit=${c.hash}`;
      link.style.textDecoration = 'none'; // opcional
      link.style.color = 'inherit';


      const circle = el('div', 'commit-circle', `C${i + 1}`);
      link.appendChild(circle);
      node.appendChild(link);
      

      /* MONSTRAMOS LA TOOLTIP CUANDO SE PASE EL RATON POR ENCIMA */
      const files = Array.isArray(c.files) ? c.files.map(f => f.file).join(', ') : '—';
      const tip = el('div', 'tooltip');
      tip.innerHTML = `
        <strong>Hash:</strong><br><code>${c.hash.slice(0,10)}…</code><br>
        <strong>Author:</strong>${authorName}<br>
        <strong>Fecha:</strong> ${new Date(c.date).toLocaleDateString()}<br>
        <strong>Fichero(s):</strong> ${files}<br><br>
        <em>${c.message}</em>
      `;
      node.appendChild(tip);

      timeline.appendChild(node);
    });

    /* NODO FIN */
    const endPosClass = (commits.length % 2 === 0) ? 'top' : 'bottom';
    const end = el('div', `commit-node ${endPosClass} end-node`);
    end.appendChild(el('div', 'commit-circle', 'FIN'));
    timeline.appendChild(end);


    const totalNodes = commits.length + 2; /* INICIO + FIN */
    timeline.style.minWidth = `${totalNodes * 220}px`;

    /* SCROLL HORINZONTAL CON LA RUEDA DEL RATON */
    const wrapper = document.querySelector('.timeline-wrapper');
    wrapper.addEventListener('wheel', e => {
      wrapper.scrollLeft += e.deltaY;
      e.preventDefault();
    }, { passive:false });
  })
  .catch(err => console.error('Error cargando commits:', err));
