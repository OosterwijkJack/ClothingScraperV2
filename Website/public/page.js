

  brands = [
        "Plein",
        "Givenchy",
        "Hood By Air",
        "Saint Laurent",
        "Balenciaga",
        "Rick Owen",
        "Maison Margiela",
        "Dolce & Gabbana",
        "Balmain",
        "291295 homme",
        "Blackmeans",
        "Dsquared2",
        "Carol Christian Poell",
        "C.P. Company",
        "Ato",
        "Matsumoto",
        "Buffalo Bobs",
        "Roberto Cavalli",
        "Amiri",
        "Dirk Bikkembergs",
        "in the attic",
        "semantic design",
        "Jun Takahashi",
        "Telfar",
        "Commes Des Garcons",
        "Cinzia Araia",
        "Acne Studios",
        "Jean Paul Gaultier",
        "Undercover",
        "PPFM",
        "LGB",
        "KMrii",
        "Share Spirit",
        "5351 Pour Les Hommes",
        "Les hommes",
        "Kapital",
        "Alexander Mcqueen",
        "Murder License",
        "Jeremy scott",
        "Vivienne westwood",
        "Diesel Black and gold",
        "Giuseppe Zanotti",
        "Gucci",
        "Dior",
        "Burberry",
        "Fendi",
        "Raf Simons",
        "Hysteric Glamour",
        "Civarize",
        "Neighborhood",
        "Moose Knuckles",
        "Number Nine",
        "Old Curiosity Shop",
        "Shellac",
        "MCM",
        "Diet Butcher",
        "Enfants Riches Déprimés",
        "Gosha Rubchinskiy",
        "Boris Bidjan",
        "Julius",
        "Mastermind japan",
        "Yohji Yamamoto",
        "Final Homme",
        "Devoa",
        "Guidi",
        "Helmut Lang",
        "Maison Mihara Yasuhiro",
        "Damir Doma",
        "Haider Ackermann",
        "Craig Green",
        "Ann Demeulemeester",
        "The Viridi-anne",
        "Kazuyuki Kumagai",
        "Lad Musician",
        "Kiryuyrik",
        "Ziggy Chen",
        "Taichi Murakami",
        "Alessandro",
        "GmbH",
        "Junya Watanabe",
        "General Research"
    ]


        const ITEMS_PER_CHUNK = 20; // Number of items to load at once
        let allClothes = [];
        let currentIndex = 0;
        let isLoading = false;

        async function loadClothes() {
            const gallery = document.getElementById('gallery');
            
            try {
                const response = await fetch('/api/clothes');
                if (!response.ok) {
                    throw new Error('Failed to fetch clothes');
                }
                
                allClothes = await response.json();
                
                if (allClothes.length === 0) {
                    gallery.innerHTML = '<div class="loading">No clothes found in database</div>';
                    return;
                }
                
                gallery.innerHTML = ''; // Clear loading message
                loadNextChunk();
                setupIntersectionObserver();
                
            } catch (error) {
                console.error('Error:', error);
                gallery.innerHTML = `<div class="error">Error loading clothes: ${error.message}</div>`;
            }
        }

        function loadNextChunk() {
            if (isLoading || currentIndex >= allClothes.length) return;
            
            isLoading = true;
            const gallery = document.getElementById('gallery');
            const endIndex = Math.min(currentIndex + ITEMS_PER_CHUNK, allClothes.length);
            const chunk = allClothes.slice(currentIndex, endIndex);
            
            const fragment = document.createDocumentFragment();
            
            chunk.forEach(item => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <a href="${item.link}" target="_blank" class="card-image">
                        <img data-src="${item.img_link}" alt="${item.description}" class="lazy-image"
                             src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23f0f0f0' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='%23999' font-family='sans-serif' font-size='14'%3ELoading...%3C/text%3E%3C/svg%3E"
                             onerror="this.src='https://via.placeholder.com/200x200?text=Image+Not+Found'">
                    </a>
                    <div class="card-content">
                        <div class="label">Price</div>
                        <div class="price">$${parseFloat(item.price).toFixed(2)}</div>
                        <div class="label">Description</div>
                        <div class="description">${item.description}</div>
                    </div>
                `;
                fragment.appendChild(card);
            });
            
            gallery.appendChild(fragment);
            currentIndex = endIndex;
            
            // Lazy load images for the new chunk
            lazyLoadImages();
            
            isLoading = false;
        }

        function lazyLoadImages() {
            const images = document.querySelectorAll('img.lazy-image[data-src]');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.remove('lazy-image');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px' // Start loading when image is 50px away from viewport
            });
            
            images.forEach(img => imageObserver.observe(img));
        }

        function setupIntersectionObserver() {
            const sentinel = document.createElement('div');
            sentinel.id = 'sentinel';
            sentinel.style.height = '20px';
            document.querySelector('.container').appendChild(sentinel);
            
            const sentinelObserver = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && currentIndex < allClothes.length) {
                    loadNextChunk();
                }
            }, {
                rootMargin: '200px' // Load more items when sentinel is 200px away
            });
            
            sentinelObserver.observe(sentinel);
        }
        document.getElementById("kill").addEventListener("click", async () => {
            await fetch("api/clothes/kill");
            window.location.reload()
        })
        async function initPage(){
            const select = document.getElementById("brand-select")

            brands.forEach(brand => {
                const option = document.createElement("option")
                option.value = brand
                option.text = brand
                select.appendChild(option)
            });

            const brandEnter = document.getElementById("brand-index")
            brandEnter.addEventListener("click", async () => {
                fetch("/api/clothes/index", {
                "method": "POST",
                "body": JSON.stringify({"brand": select.value}),
                "headers": {"Content-Type": "application/json"}
            })
            .then(res => res.json())
            .then(data => {
                currentIndex = data.index
                console.log(data)
                loadClothes();
            })
        })
    }

        // Load clothes when page loads
        //
initPage()
loadClothes()
        