// JS for Processing.html

<script>
    var originalImages = {{ original_images | tojson | safe }};
    var segmentedImages = {{ segmented_images | tojson | safe }};
    var lineObjects = {{ line_objects | tojson | safe }};

    var stage = new Konva.Stage({
        container: 'canvasContainer',
        width: 512,
        height: 512
    });

    var layer = new Konva.Layer();
    stage.add(layer);

    var backgroundImage = new Image();
    backgroundImage.onload = function() {
        var image = new Konva.Image({
            x: 0,
            y: 0,
            image: backgroundImage,
            width: 512,
            height: 512
        });
        layer.add(image);
        layer.draw();
    };
    backgroundImage.onerror = function() {
        console.error('Error loading background image');
    };
    
    // Load the first original image by default
    if (originalImages.length > 0) {
        backgroundImage.src = originalImages[0];
    } else {
        console.error('No original images available');
    }

    function updateBackground() {
        var selectedImages = originalImages.length > 0 ? [originalImages[0]] : [];  // Always include the original image if available
        
        if (document.getElementById('TibioCalcaneal') && document.getElementById('TibioCalcaneal').checked) {
            addSegmentedImage('tibia.jpg');
            addSegmentedImage('calcaneus.jpg');
        }
        if (document.getElementById('TaloCalcaneal') && document.getElementById('TaloCalcaneal').checked) {
            addSegmentedImage('talus.jpg');
            addSegmentedImage('calcaneus.jpg');
        }
        if (document.getElementById('CalcanealPitch') && document.getElementById('CalcanealPitch').checked) {
            addSegmentedImage('M5.jpg');
            addSegmentedImage('calcaneus.jpg');
        }
        if (document.getElementById('Meary') && document.getElementById('Meary').checked) {
            addSegmentedImage('M1.jpg');
            addSegmentedImage('calcaneus.jpg');
        }
        if ((document.getElementById('Gissane') && document.getElementById('Gissane').checked) || 
            (document.getElementById('Bohler') && document.getElementById('Bohler').checked)) {
            addSegmentedImage('calcaneus.jpg');
        }

        function addSegmentedImage(imageName) {
            var segmentedImage = Object.values(segmentedImages)[0].find(img => img.includes(imageName));
            if (segmentedImage) {
                selectedImages.push(segmentedImage);
            }
        }

        // Remove duplicates
        selectedImages = [...new Set(selectedImages)];

        // Load and merge selected images
        Promise.all(selectedImages.map(src => 
            new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = src;
            })
        )).then(images => {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');
            images.forEach(img => {
                ctx.globalAlpha = 1 / images.length;
                ctx.drawImage(img, 0, 0, 512, 512);
            });
            backgroundImage.src = canvas.toDataURL();
        }).catch(error => {
            console.error('Error loading images:', error);
        });
    }

    // Add event listeners to checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateBackground);
    });

    // Draw lines
    function drawLines() {
        if (Object.keys(lineObjects).length > 0) {
            const firstImageLines = Object.values(lineObjects)[0];
            if (firstImageLines && firstImageLines.lines) {
                firstImageLines.lines.forEach(line => {
                    var konvaLine = new Konva.Line({
                        points: [line.start.x, line.start.y, line.end.x, line.end.y],
                        stroke: line.color,
                        strokeWidth: line.thickness,
                    });
                    layer.add(konvaLine);
                });
                layer.draw();
            }
        }
    }

    // Call drawLines after the background image has loaded
    backgroundImage.onload = function() {
        var image = new Konva.Image({
            x: 0,
            y: 0,
            image: backgroundImage,
            width: 512,
            height: 512
        });
        layer.add(image);
        drawLines();
        layer.draw();
    };
</script>