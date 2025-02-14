
    const apiKey = '8809a7e7d76f40869517d14b352d536f'; // Replace with your OpenCage API key
    const inputField = document.getElementById('city');
    const autocompleteList = document.getElementById('autocomplete-list');
    

    // Function to fetch autocomplete suggestions
    function fetchSuggestions(query) {
      console.log ("inside java script autocomplete");
      const url = `https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(query)}&key=${apiKey}&language=en&limit=5`;
      fetch(url)
        .then(response => response.json())
        .then(data => {
          displaySuggestions(data.results);
        })
        .catch(error => {
          console.error('Error fetching data from OpenCage:', error);
        });
    }

    // Display the fetched suggestions
    function displaySuggestions(suggestions) {
      autocompleteList.innerHTML = ''; // Clear previous suggestions

      if (suggestions.length === 0) {
        return;
      }

      suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.classList.add('autocomplete-item');
        item.textContent = suggestion.formatted;

        // Add click event to handle item selection
        item.addEventListener('click', () => {
          inputField.value = suggestion.formatted; // Set the selected suggestion
          autocompleteList.innerHTML = ''; // Clear the suggestions list
        });

        autocompleteList.appendChild(item);
      });
    }

    // Event listener to handle user input
    inputField.addEventListener('input', (e) => {
      const query = e.target.value;

      // Only fetch suggestions if query length is greater than 2
      if (query.length > 2) {
        fetchSuggestions(query);
      } else {
        autocompleteList.innerHTML = ''; // Clear suggestions if input is too short
      }
    });

    // Close the suggestions list if the user clicks outside
    document.addEventListener('click', (e) => {
      if (!autocompleteList.contains(e.target) && e.target !== inputField) {
        autocompleteList.innerHTML = '';
      }
    });
  