window.onload = function() {

    function updateSignal() {
        fetch('/get_signal')
            .then(response => response.json())
            .then(data => {
                let signalValue = data.signal;
                let container = document.getElementById('signal-container');

                container.innerHTML = '';

                for (let i = 1; i <= 5; i++) {
                    let bar = document.createElement('div');
                    bar.className = (i <= signalValue) ? 'bar active' : 'bar';
                    bar.style.height = (i * 5) + 'px'; 
                    container.appendChild(bar);
                }
            })
            .catch(error => console.error('Error fetching signal:', error))
            .finally(updateStatus);
    }

    function updateStatus() {
        $.getJSON('/status', function(data) {
            $('#status').text(data.status);
        }).always(updateLatency);
    }

    function updateLatency() {
        $.getJSON('/latency', function(data) {
            $('#latency').text(`${data.latency} ms`);
        }).always(() => setTimeout(updateSignal, 15000)); 
    }

    updateSignal();
};
