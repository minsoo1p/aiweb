// Define color mapping for each segment
const segmentColors = {
    'calcaneus.jpg': {r: 255, g: 0, b: 0},    // Red
    'M1.jpg': {r: 0, g: 0, b: 255},           // Blue
    'tibia.jpg': {r: 0, g: 255, b: 0},        // Green
    'talus.jpg': {r: 255, g: 255, b: 0},      // Yellow
    'M5.jpg': {r: 255, g: 0, b: 255},         // Magenta
};

var container = document.getElementById('canvasContainer');
var containerWidth = container.offsetWidth;

var stage = new Konva.Stage({
    container: 'canvasContainer',
    width: containerWidth,
    height: containerWidth
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
    var originalImage = originalImages.length > 0 ? originalImages[0] : null;
    var selectedSegmentedImages = [];
    
    if (document.getElementById('TibioCalcaneal') && document.getElementById('TibioCalcaneal').checked) {
        addSegmentedImage('tibia.jpg');
        addSegmentedImage('calcaneus.jpg');
    }
    if (document.getElementById('TaloCalcaneal') && document.getElementById('TaloCalcaneal').checked) {
        addSegmentedImage('talus.jpg');
        addSegmentedImage('calcaneus.jpg');
    }
    if (document.getElementById('Calcaneal Pitch') && document.getElementById('Calcaneal Pitch').checked) {
        addSegmentedImage('M5.jpg');
        addSegmentedImage('calcaneus.jpg');
    }
    if (document.getElementById('Meary') && document.getElementById('Meary').checked) {
        addSegmentedImage('M1.jpg');
        addSegmentedImage('calcaneus.jpg');
    }
    if ((document.getElementById('Gissane') && document.getElementById('Gissane').checked) || 
        (document.getElementById('Böhler') && document.getElementById('Böhler').checked)) {
        addSegmentedImage('calcaneus.jpg');
    }

    function addSegmentedImage(imageName) {
        var segmentedImage = Object.values(segmentedImages)[0].find(img => img.includes(imageName));
        if (segmentedImage && !selectedSegmentedImages.includes(segmentedImage)) {
            selectedSegmentedImages.push({src: segmentedImage, name: imageName});
        }
    }

    // Load and process images
    Promise.all([
        new Promise((resolve, reject) => {
            if (originalImage) {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = originalImage;
            } else {
                resolve(null);
            }
        }),
        ...selectedSegmentedImages.map(img => 
            new Promise((resolve, reject) => {
                const image = new Image();
                image.onload = () => resolve({image: image, name: img.name});
                image.onerror = reject;
                image.src = img.src;
            })
        )
    ]).then(images => {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        // Draw original image at full opacity
        if (images[0]) {
            ctx.globalAlpha = 1;
            ctx.drawImage(images[0], 0, 0, 512, 512);
        }

        // Process and draw segmented images
        for (let i = 1; i < images.length; i++) {
            const segmentedCanvas = document.createElement('canvas');
            segmentedCanvas.width = 512;
            segmentedCanvas.height = 512;
            const segmentedCtx = segmentedCanvas.getContext('2d');
            
            segmentedCtx.drawImage(images[i].image, 0, 0, 512, 512);
            const imageData = segmentedCtx.getImageData(0, 0, 512, 512);
            const data = imageData.data;

            const color = segmentColors[images[i].name] || {r: 128, g: 128, b: 128}; // Default to gray if color not found

            for (let j = 0; j < data.length; j += 4) {
                if (data[j] === 0 && data[j+1] === 0 && data[j+2] === 0) {
                    // Change black background to white
                    data[j] = 255;
                    data[j+1] = 255;
                    data[j+2] = 255;
                    data[j+3] = 0;  // Make it transparent
                } else {
                    // Apply specific color to the bone mask
                    data[j] = color.r;
                    data[j+1] = color.g;
                    data[j+2] = color.b;
                    data[j+3] = 128;  // Semi-transparent
                }
            }

            segmentedCtx.putImageData(imageData, 0, 0);

            // Draw the processed segmented image onto the main canvas
            ctx.globalAlpha = 0.5;
            ctx.drawImage(segmentedCanvas, 0, 0, 512, 512);
        }

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
            firstImageLines.lines.forEach((line, index) => {
                var konvaLine = new Konva.Line({
                    points: [line.start.x, line.start.y, line.end.x, line.end.y],
                    stroke: line.color,
                    strokeWidth: line.thickness,
                });

                var startAnchor = new Konva.Circle({
                    x: line.start.x,
                    y: line.start.y,
                    radius: 5,
                    fill: 'white',
                    stroke: line.color,
                    strokeWidth: 2,
                    draggable: true,
                });

                var endAnchor = new Konva.Circle({
                    x: line.end.x,
                    y: line.end.y,
                    radius: 5,
                    fill: 'white',
                    stroke: line.color,
                    strokeWidth: 2,
                    draggable: true,
                });

                var group = new Konva.Group({
                    draggable: true,
                });
                group.add(konvaLine);
                group.add(startAnchor);
                group.add(endAnchor);
                layer.add(group);

                function updateAnchors() {
                    var groupPos = group.position();
                    var points = konvaLine.points();
                    startAnchor.position({
                        x: points[0] + groupPos.x,
                        y: points[1] + groupPos.y
                    });
                    endAnchor.position({
                        x: points[2] + groupPos.x,
                        y: points[3] + groupPos.y
                    });
                }

                startAnchor.on('dragmove', function() {
                    var groupPos = group.position();
                    var points = konvaLine.points();
                    points[0] = startAnchor.x() - groupPos.x;
                    points[1] = startAnchor.y() - groupPos.y;
                    konvaLine.points(points);
                    layer.batchDraw();
                });

                endAnchor.on('dragmove', function() {
                    var groupPos = group.position();
                    var points = konvaLine.points();
                    points[2] = endAnchor.x() - groupPos.x;
                    points[3] = endAnchor.y() - groupPos.y;
                    konvaLine.points(points);
                    layer.batchDraw();
                });

                group.on('dragmove', function() {
                    updateAnchors();
                });

                group.on('dragend', function() {
                    updateLineObject(index, konvaLine, group);
                });

                startAnchor.on('dragend', endAnchor.on('dragend', function() {
                    updateLineObject(index, konvaLine, group);
                }));

                group.on('mouseenter', function() {
                    stage.container().style.cursor = 'move';
                });

                group.on('mouseleave', function() {
                    stage.container().style.cursor = 'default';
                });

                startAnchor.on('mouseenter', function() {
                    stage.container().style.cursor = 'pointer';
                });

                endAnchor.on('mouseenter', function() {
                    stage.container().style.cursor = 'pointer';
                });
            });
            layer.draw();
        }
    }
}

function updateLineObject(index, konvaLine, group) {
    var points = konvaLine.points();
    var groupPos = group.position();
    var lineObject = Object.values(lineObjects)[0].lines[index];
    lineObject.start = { x: points[0] + groupPos.x, y: points[1] + groupPos.y };
    lineObject.end = { x: points[2] + groupPos.x, y: points[3] + groupPos.y };
    console.log('Updated line object:', lineObject);
}

function rotatePoint(point, pivot, angle) {
    var radians = (Math.PI / 180) * angle,
        cos = Math.cos(radians),
        sin = Math.sin(radians),
        nx = (cos * (point.x - pivot.x)) + (sin * (point.y - pivot.y)) + pivot.x,
        ny = (cos * (point.y - pivot.y)) - (sin * (point.x - pivot.x)) + pivot.y;
    return {x: nx, y: ny};
}

// Call drawLines after the background image has loaded
backgroundImage.onload = function() {
    var image = new Konva.Image({
        x: 0,
        y: 0,
        image: backgroundImage,
        width: stage.width(),
        height: stage.height()
    });
    layer.add(image);
    drawLines();
    layer.draw();
};