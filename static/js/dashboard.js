document.addEventListener("DOMContentLoaded", () => {
    const selectAll = document.getElementById("select-all");
    const checkboxes = document.querySelectorAll('input[name="cities"]');

    if (selectAll) {
        selectAll.addEventListener("change", () => {
          checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }

    function handleExport(formId, errorId) {
        const form = document.getElementById(formId);
        const errorBox = document.getElementById(errorId);

        if (!form) return;

        form.addEventListener("submit", async (e) => {
            e.preventDefault(); // stop page reload
            errorBox.textContent = "";

            const formData = new FormData(form);

            try {
                const response = await fetch(form.action, {method: "POST",body: formData});

                if (!response.ok) {
                    const data = await response.json();
                    errorBox.textContent = data.error;
                    return;
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");

                a.href = url;
                a.download = response.headers.get("Content-Disposition")?.split("filename=")[1]?.replace(/"/g, "") || "download";

                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (err) {
                errorBox.textContent = "Unexpected error. Try again.";
            }
        });
    }
    checkboxes.forEach(cb => {
        cb.addEventListener("change", () => {
            const csvError = document.getElementById("csvError");
            if (csvError) csvError.textContent = "";
        });
    });

    handleExport("csvForm", "csvError");
    handleExport("plotForm", "plotError");


    const searchForm = document.querySelector(".search-bar");
    const searchError = document.getElementById("searchError");

    if (searchForm) {
        searchForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            searchError.textContent = "";

            const formData = new FormData(searchForm);
            const params = new URLSearchParams(formData);

            try {
                const res = await fetch("/?" + params.toString(), {headers: { "X-Requested-With": "XMLHttpRequest" }});

                const data = await res.json();

                if (data.warning) {
                    searchError.textContent = data.warning;
                } else {
                    // Clear error
                    searchError.textContent = "";

                    // Update table
                    const tbody = document.querySelector("table tbody");
                    if (tbody) {
                        tbody.innerHTML = "";
                        data.tables.forEach(row => {
                            const tr = document.createElement("tr");
                            tr.innerHTML = `<td><input type="checkbox" name="cities" value="${row.City}"></td><td><a href="/city/${encodeURIComponent(row.City)}">${row.City}</a></td><td>${row.Country}</td><td>${row.Population}</td><td>${row.Area_km2}</td><td class="${row.PopulationDensity && row.PopulationDensity > 10000 ? "dense" : ""}">${row.PopulationDensity || "—"}</td><td>${row.Average_Temp_C}</td>`;
                            tbody.appendChild(tr);
                        });
                    }

                    // Update plot
                    const plotImg = document.querySelector(".plot-wrapper img");
                    if (plotImg && data.plot) {
                        plotImg.src = `data:image/png;base64,${data.plot}`;
                    }
                }

            } catch {
                searchError.textContent = "Unexpected error. Please try again.";
            }
        });
        searchForm.querySelector("input[name='q']").addEventListener("input", () => {
            searchError.textContent = "";
        });

    }

});
