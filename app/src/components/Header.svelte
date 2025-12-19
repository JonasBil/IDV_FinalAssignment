<script>
  let showModal = false;

  function toggleModal() {
    showModal = !showModal;
  }
</script>

<header>
  <div class="logo">IDV Final Project</div>
  <nav>
    <button class="about-btn" on:click={toggleModal}>About</button>
  </nav>
</header>

{#if showModal}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="modal-backdrop" on:click={toggleModal}>
    <div class="modal-content" on:click|stopPropagation>
      <button class="close-btn" on:click={toggleModal}>&times;</button>
      <h2>About This Project</h2>
      
      <div class="modal-body">
        <h3>The Assignment</h3>
        <p>
          This visualization was developed as a final project for the Interactive Data Visualization (IDV) course. 
          The assignment was to create multiple visualizations based on a specific dataset. 
        </p>

        <h3>The Data</h3>
        <p>
          We choose the <strong>Mapping Diversity</strong> dataset, created by the European Data Journalism Network for our visualizations. 
          This dataset was created to discover key facts about diversity and representation in street names across Europe and to start a debate.
        </p>
        <p>
          The dataset includes an analysis of over <strong>145,000 streets</strong> across <strong>32 European cities</strong>. 
          It provides information for every street, including:
        </p>
        <ul>
          <li>The street's name and location (City, Country).</li>
          <li>Whether it is named after a person.</li>
          <li>The person's gender, occupation, date of birth, and other attributes sourced from Wikidata.</li>
        </ul>
        
        <p>
          More information about the dataset can be found <a href="https://mappingdiversity.eu/about/" target="_blank" rel="noopener noreferrer">here</a>, 
          and the dataset can be downloaded <a href="https://drive.google.com/drive/folders/1xBc8EcR2jR2senxMpgIRFE0jafMn23sM" target="_blank" rel="noopener noreferrer">here</a>.
        </p>
      </div>
    </div>
  </div>
{/if}

<style>
  header {
    background: #1f2937;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #374151;
  }
  .logo {
    font-weight: bold;
    font-size: 1.2rem;
    color: #fb923c;
  }
  .about-btn {
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    font-size: 1rem;
    margin-left: 1rem;
    padding: 0;
    text-decoration: none;
  }
  .about-btn:hover {
    color: #f3f4f6;
    text-decoration: underline;
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .modal-content {
    background: #1f2937; /* Dark theme matching header */
    color: #f3f4f6;
    padding: 2.5rem;
    border-radius: 12px;
    width: 90%;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    border: 1px solid #374151;
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    background: none;
    border: none;
    color: #9ca3af;
    font-size: 2rem;
    cursor: pointer;
    line-height: 1;
  }
  
  .close-btn:hover {
    color: #fff;
  }

  h2 {
    margin-top: 0;
    color: #fb923c;
    font-size: 2rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #374151;
    padding-bottom: 1rem;
  }

  h3 {
    color: #e5e7eb;
    margin-top: 1.5rem;
    font-size: 1.3rem;
  }

  p {
    line-height: 1.6;
    color: #d1d5db;
    margin-bottom: 1rem;
    font-size: 1.05rem;
  }

  ul {
    list-style-type: disc;
    margin-left: 1.5rem;
    color: #d1d5db;
    margin-bottom: 1rem;
  }

  li {
    margin-bottom: 0.5rem;
  }
  
  strong {
    color: #f3f4f6;
  }
  
  em {
    color: #9ca3af;
  }

  .modal-body a {
    color: #fb923c;
    text-decoration: underline;
  }

  .modal-body a:hover {
    color: #f3f4f6;
  }
</style>
