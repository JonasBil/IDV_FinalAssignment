<script>
  import { selectedCities } from '../stores/compareSelection.js';
  
  let showExample = false;

  function toggleExample() {
    showExample = !showExample;
    if (showExample) {
      // Set Copenhagen and Chisinau as selected cities
      selectedCities.set(['københavn', 'chisinau']);
    } else {
      // Clear selection when hiding the example
      selectedCities.clear();
    }
  }
</script>

<div class="intro">
  <h1>Who gets remembered in our streets?</h1>

  <!-- ALGEMENE INTRO -->
  <p>
    For centuries, women across Europe were denied fundamental rights to work,
    political positions, and public recognition.
    Their labour, whether it was intellectual, cultural, or political, was often
    undervalued for commemoration. As a result, women were systematically excluded
    from the symbolic spaces through which societies remember their past.

    This exclusion is clearly visible in something as ordinary as street names.
    Streets are daily points of reference, shaping how history is encountered and
    normalised in public space. The overwhelming dominance of male names, and the
    marginal presence of women, exposes how deeply gender inequality is embedded
    in the urban landscape.
  </p>

  <p>
    This website documents streets named after people across multiple European cities.
    For each street, it identifies whether it is eponymic and, if so, provides
    information on the person commemorated, including gender, occupation, year of
    birth, and nationality. The data is primarily derived from Wikidata and has been
    standardised to enable systematic comparison between cities.

    By visualising who is recognised and who is not, the platform reveals how
    historical restrictions on women’s access to work, power, and visibility
    continue to shape present-day cities.
  </p>

  <!-- KNOP -->
  <button class="toggle-btn" on:click={toggleExample}>
    {showExample ? 'Hide example' : 'Show example: Copenhagen vs Chișinău'}
  </button>

  <!-- VERDIEPING -->
  {#if showExample}
    <div class="example">
      <p>
        To illustrate this, the comparison between <strong>Copenhagen</strong> and
        <strong>Chișinău</strong> can be taken as an example.

        In <strong>Copenhagen</strong>, … streets are named after people,
        <span class="blue_bold">...</span> honour <span class="blue_bold">men</span>,
        while <span class="orange_bold">...</span> are named after
        <span class="orange_bold">women</span>, corresponding to <strong>...%</strong>.

        In <strong>Chișinău</strong>, the imbalance is even sharper.
        Out of … eponymic streets, <span class="blue_bold">...</span> are named after
        <span class="blue_bold">men</span>, while <span class="orange_bold">...</span> are named after
        <span class="orange_bold">women</span>, which is less than <strong>...%</strong>.
      </p>

      <p>
        Beyond numbers, the occupation of women remembered in the streets differs
        strongly. In Copenhagen, most streets are associated with
        <strong>politics (40.6%)</strong>, while in Chișinău
        <strong>culture (60%)</strong> dominates.

        These differences are also visible across time. Women commemorated in
        Copenhagen were born, on average, around <strong>1865</strong>, whereas in
        Chișinău the average birth year is considerably later, around
        <strong>1913</strong>.
      </p>

      <p>
        Nationality further sharpens this contrast. In Copenhagen,
        <strong>63.9%</strong> of streets named after women honour figures of
        <strong>Danish</strong> origin. In Chișinău, only <strong>16.3%</strong>
        refer to women from <strong>Moldova</strong>, pointing to more external figures.

        Together, these contrasts raise important questions: whose histories are
        celebrated, for which roles women are remembered, and how local and national
        identities are inscribed into the urban landscape.
      </p>
    </div>
  {/if}

  <p class="cta">
    Explore more below...
  </p>
</div>

<style>
  .intro {
    max-width: 1000px;
    margin: 3rem auto 2rem;
    padding: 0 1.5rem;
    color: #e5e7eb;
    text-align: center;
  }

  .toggle-btn {
    margin: 1.5rem auto;
    padding: 0.6rem 1.2rem;
    border-radius: 999px;
    border: 1px solid #f59e0b;
    background: transparent;
    color: #f59e0b;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.2s ease, color 0.2s ease;
  }

  .toggle-btn:hover {
    background: #f59e0b;
    color: #111827;
  }

  .example {
    margin-top: 1.5rem;
    animation: fadeIn 0.3s ease-in-out;
  }

  .cta {
    font-size: 0.95rem;
    color: #9ca3af;
    font-style: italic;
    margin-top: 2rem;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-5px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>


