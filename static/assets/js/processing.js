// Define mapping as constant
const segmentColors = {
    'cal': {r: 255, g: 0, b: 0},    // Red
    'm1': {r: 0, g: 0, b: 255},           // Blue
    'tib': {r: 0, g: 255, b: 0},        // Green
    'tal': {r: 255, g: 255, b: 0},      // Yellow
    'm5': {r: 255, g: 0, b: 255},         // Magenta
};

const angleMapping = {
    'TibioCalcaneal': 'tibiocalcaneal',
    'TaloCalcaneal': 'talocalcaneal',
    'Calcaneal Pitch': 'calcanealpitch',
    'Meary': 'meary',
    'Gissane': 'gissane',
    'Böhler': 'bohler'
};

var global_id = 0;
var angleTag = null
var currentAngles = {};

// Define canvas setting of main canvas
var container = document.getElementById('canvasContainer');
var containerWidth = container.offsetWidth;

var stage = new Konva.Stage({
    container: 'canvasContainer',
    width: containerWidth,
    height: containerWidth
});
var layer = new Konva.Layer();
stage.add(layer);

// Define canvas setting of modal canvas
var stageLarge, layerLarge;

// Canvas 동기화 함수
function syncLines(targetLayer, angleTag) {
    if (!angleTag) {
        throw new Error("No angle tag provided for synchronization");
    }

    const angleName = angleMapping[angleTag];

    const lines = targetLayer.find('Line');
    if (lines.length !== 2) {
        throw new Error(`Expected 2 lines for ${angleTag}, but found ${lines.length}`);
    }

    const line_scaler = (targetLayer === layerLarge) ? 0.5 : 1;

    const updatedLines = lines.map(line => {
        const points = line.points();

        return {
            start: {
                x: points[0] * line_scaler,
                y: points[1] * line_scaler
            },
            end: {
                x: points[2] * line_scaler,
                y: points[3] * line_scaler
            }
        };
    });

    lineObjects[Object.keys(lineObjects)[global_id]][angleName] = updatedLines;
}

document.getElementById('staticBackdrop').addEventListener('shown.bs.modal', function ()  {
    syncLines(layer, angleTag);

    var containerLarge = document.getElementById('canvasContainerLarge');
    var containerLargeWidth = containerLarge.offsetWidth;

    if (!stageLarge) {
        stageLarge = new Konva.Stage({
            container: 'canvasContainerLarge',
            width: containerLargeWidth,
            height: containerLargeWidth
        });
        layerLarge = new Konva.Layer();
        stageLarge.add(layerLarge);
    } else {
        stageLarge.width(containerLargeWidth);
        stageLarge.height(containerLargeWidth);
    }

    updateBackground(stageLarge, layerLarge);
});

function saveExpandedImage() {
    syncLines(layerLarge, angleTag);
    updateBackground(stage, layer);
    var myModalEl = document.getElementById('staticBackdrop');
    var modal = bootstrap.Modal.getInstance(myModalEl);
    modal.hide();
}

var backgroundImage = new Image();


// Load the first original image by default
if (originalImages.length > 0) {
    backgroundImage.src = originalImages[global_id];
} else {
    console.error('No original images available');
}

function updateBackground(targetStage, targetLayer) {
    var originalImage = originalImages.length > 0 ? originalImages[global_id] : null;
    var selectedSegmentedImages = [];

    function addSegmentedImage(imageName) {
        var segmentedImage = segmentedImages[Object.keys(segmentedImages)[global_id]];
        if (segmentedImage && segmentedImage[imageName]) {
            selectedSegmentedImages.push({src: segmentedImage[imageName], name: imageName});
        }
    }
    
    if (document.getElementById('TibioCalcaneal') && document.getElementById('TibioCalcaneal').checked) {
        addSegmentedImage('tib');
        addSegmentedImage('cal');
    }
    if (document.getElementById('TaloCalcaneal') && document.getElementById('TaloCalcaneal').checked) {
        addSegmentedImage('tal');
        addSegmentedImage('cal');
    }
    if (document.getElementById('Calcaneal Pitch') && document.getElementById('Calcaneal Pitch').checked) {
        addSegmentedImage('m5');
        addSegmentedImage('cal');
    }
    if (document.getElementById('Meary') && document.getElementById('Meary').checked) {
        addSegmentedImage('m1');
        addSegmentedImage('tal');
    }
    if ((document.getElementById('Gissane') && document.getElementById('Gissane').checked) || 
        (document.getElementById('Böhler') && document.getElementById('Böhler').checked)) {
        addSegmentedImage('cal');
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
        canvas.width = 528;
        canvas.height = 528;
        const ctx = canvas.getContext('2d');

        // Draw original image at full opacity
        if (images[0]) {
            ctx.globalAlpha = 1;
            ctx.drawImage(images[0], 0, 0, 528, 528);
        }

        // Process and draw segmented images
        for (let i = 1; i < images.length; i++) {
            const segmentedCanvas = document.createElement('canvas');
            segmentedCanvas.width = 528;
            segmentedCanvas.height = 528;
            const segmentedCtx = segmentedCanvas.getContext('2d');
            
            segmentedCtx.drawImage(images[i].image, 0, 0, 528, 528);
            const imageData = segmentedCtx.getImageData(0, 0, 528, 528);
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
            ctx.drawImage(segmentedCanvas, 0, 0, 528, 528);
        }

        backgroundImage.src = canvas.toDataURL();
        backgroundImage.onload = function() {
            updateCanvasWithBackground(targetStage, targetLayer);
        };

    }).catch(error => {
        console.error('Error loading images:', error);
    });
}

function updateCanvasWithBackground(targetStage, targetLayer) {
    var target_images = targetLayer.find('Image');
    target_images.forEach(image => image.destroy());
    // var target_groups = targetLayer.find('Group');
    // target_groups.forEach(group => group.destroy());

    var image = new Konva.Image({
        x: 0,
        y: 0,
        image: backgroundImage,
        width: targetStage.width(),
        height: targetStage.height()
    });
    targetLayer.add(image);
    drawLines(targetStage, targetLayer);
    targetLayer.draw();
}

// Add event listeners to checkboxes
document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            angleTag = this.id;
        } else {
            angleTag = null;
        }

        document.querySelectorAll('input[type="checkbox"]').forEach(otherCheckbox => {
            if (otherCheckbox !== this) {
                otherCheckbox.checked = false;
            }
        });

        updateBackground(stage, layer);
    });
});

function confirmSave() {
    let table = document.getElementById('dataTable');
    let currentRow = table.rows[global_id + 1]; 

    for (let [key, value] of Object.entries(currentAngles)) {
        let cell = currentRow.querySelector(`td[data-angle="${key}"]`);
        if (cell) {
            cell.textContent = value.toFixed(1);
        }
    }

    if (global_id < originalImages.length - 1) {
        global_id++;
        updateAllCanvases();
    } else {
        alert("You have reached the last image.");
    }
}

function saveAndExportData() {
    let table = document.getElementById('dataTable');
    let data = [];

    for (let i = 1; i < table.rows.length; i++) {
        let row = table.rows[i];
        let rowData = {
            id: row.getAttribute('data-id'),
            image_name: row.cells[0].textContent
        };

        for (let j = 1; j < row.cells.length; j++) {
            let cell = row.cells[j];
            let angleType = cell.getAttribute('data-angle');
            rowData[angleType] = parseFloat(cell.textContent) || null;
        }

        data.push(rowData);
    }

    fetch('/save_data_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Data saved successfully!');
        } else {
            alert('Error saving data.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error saving data.');
    });
}

// Draw lines
function drawLines(stage, layer) {
    layer.find('Group').forEach(group => group.destroy());

    const angle_list = ['TibioCalcaneal', 'TaloCalcaneal', 'Calcaneal Pitch', 'Meary', 'Gissane', 'Böhler'];

    angle_list.forEach(angle =>{
        if (document.getElementById(angle).checked) {
            drawLinesForAngle(angleMapping[angle], stage, layer);
        }
    })
}

function drawLinesForAngle(angleName, stage, layer) {
    var lineObject = lineObjects[Object.keys(lineObjects)[global_id]];
    if (lineObject && lineObject[angleName]) {
        var lines = lineFitting(lineObject[angleName], canvasSize=stage.width());
        var groups = [];
        
        lines.forEach((line, index) => {
            var konvaLine = new Konva.Line({
                points: [line.start.x, line.start.y, line.end.x, line.end.y],
                stroke: 'yellow',
                strokeWidth: 2,
            });

            var startAnchor = new Konva.Circle({
                x: line.start.x,
                y: line.start.y,
                radius: 3,
                fill: 'white',
                stroke: 'green',
                strokeWidth: 2,
                draggable: true,
            });

            var endAnchor = new Konva.Circle({
                x: line.end.x,
                y: line.end.y,
                radius: 3,
                fill: 'white',
                stroke: 'green',
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
            groups.push(group);

            function updateLine() {
                var points = [
                    startAnchor.x(),
                    startAnchor.y(),
                    endAnchor.x(),
                    endAnchor.y()
                ];
                konvaLine.points(points);
            }

            function addDragBehavior(shape) {
                var isDragging = false;
                
                shape.on('mousedown touchstart', function() {
                    isDragging = true;
                });

                shape.on('mouseup touchend', function() {
                    isDragging = false;
                    updateLineObject(lines, index, konvaLine, group, layer, angleName);
                });

                shape.on('dragmove', function() {
                    updateLine();
                    updateLineObject(lines, index, konvaLine, group, layer, angleName);
                });

                stage.on('mouseout', function() {
                    if (isDragging) {
                        isDragging = false;
                        updateLineObject(lines, index, konvaLine, group, layer, angleName);
                    }
                });
            }

            addDragBehavior(group);
            addDragBehavior(startAnchor);
            addDragBehavior(endAnchor);

            startAnchor.on('dragmove', function() {
                updateLine();
                layer.batchDraw();
            });

            endAnchor.on('dragmove', function() {
                updateLine();
                layer.batchDraw();
            });

            group.on('dragmove', function() {
                layer.batchDraw();
            });

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

        if (lines.length === 2) {
            var angle = calculateAngleBetweenLines(lines[0], lines[1]);
            displayAngle(angle, lines[0], lines[1], layer);
        }
    }
};

function displayAngle(angle, line1, line2, layer) {
    layer.find('Text').forEach(text => text.destroy());
    layer.find('Arc').forEach(arc => arc.destroy());

    let currentAngleType = null;
    for (let [key, value] of Object.entries(angleMapping)) {
        if (document.getElementById(key).checked) {
            currentAngleType = value;
            break;
        }
    }

    if (currentAngleType) {
        currentAngles[currentAngleType] = parseFloat(angle);
    }
    
    const x1 = line1.start.x, y1 = line1.start.y;
    const x2 = line1.end.x, y2 = line1.end.y;
    const x3 = line2.start.x, y3 = line2.start.y;
    const x4 = line2.end.x, y4 = line2.end.y;

    const denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);

    const t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator;
    const u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator;

    if (denominator ===0) {
        var center = null;
    } else {
        var center = {
            x: x1 + t * (x2 - x1),
            y: y1 + t * (y2 - y1)
        };
    }
    const slope1 = (line1.end.y - line1.start.y) / (line1.end.x - line1.start.x);
    const slope2 = (line2.end.y - line2.start.y) / (line2.end.x - line2.start.x);

    var angle1 = Math.atan(slope1) * 180/Math.PI;
    var angle2 = Math.atan(slope2) * 180/Math.PI;

    var startAngle = Math.min(angle1, angle2);
    var endAngle = Math.max(angle1, angle2);

    let konvaStartAngle;

    if (endAngle - startAngle > 90) {
        konvaStartAngle = endAngle;
    } else {
        konvaStartAngle = startAngle;
    };

    var arc = new Konva.Arc({
        x: center.x,
        y: center.y,
        innerRadius: 0,
        outerRadius: 30,
        angle: angle,
        rotation: konvaStartAngle,
        clockwise: false,
        fill: 'white',
        opacity: 0.7,
    });

    const middleAngle = (konvaStartAngle + angle / 2) * Math.PI/180;
    const textOffsetMultiplier = 1.8;
    const textX = center.x + Math.cos(middleAngle) * 30 * textOffsetMultiplier;
    const textY = center.y + Math.sin(middleAngle) * 30 * textOffsetMultiplier;

    var angleText = new Konva.Text({
        x: textX,
        y: textY,
        text: angle + '°',
        fontSize: 16,
        fill: 'white',
        align: 'center',
    });

    angleText.offsetX(angleText.width() / 2);
    angleText.offsetY(angleText.height() / 2);

    layer.add(arc);
    layer.add(angleText);
};

function updateLineObject(lines, index, konvaLine, group, layer, angleName) {
    var points = konvaLine.points();
    var groupPos = group.position();
    // const line_scaler = (layer === layerLarge) ? 0.5 : 1;

    lines[index].start = { x: points[0] + groupPos.x, y: points[1] + groupPos.y };
    lines[index].end = { x: points[2] + groupPos.x, y: points[3] + groupPos.y };

    // const updatedLines = lines.map(line => {
    //     return {
    //         start: {
    //             x: line.start.x * line_scaler,
    //             y: line.start.y * line_scaler
    //         },
    //         end: {
    //             x: line.end.x * line_scaler,
    //             y: line.end.y * line_scaler
    //         }
    //     };
    // });

    // lineObjects[Object.keys(lineObjects)[global_id]][angleName] = updatedLines;
    
    layer.find('Arc').forEach(arc => arc.destroy());
    layer.find('Text').forEach(text => text.destroy());

    if (lines.length === 2) {
        var angle = calculateAngleBetweenLines(lines[0], lines[1]);
        displayAngle(angle, lines[0], lines[1], layer);
    }
}

function lineFitting(lines, canvasSize = 528, margin = 5) {
    const scale = canvasSize / 528;

    return lines.map(line => {
        let start, end, slope;

        if ('start' in line && 'end' in line) {
            start = {
                x: line.start.x * scale,
                y: line.start.y * scale
            };
            end = {
                x: line.end.x * scale,
                y: line.end.y * scale
            };
            slope = (end.y - start.y) / (end.x - start.x);
        }
        else if ('point' in line && 'slope' in line) {
            start = {
                x: line.point.x * scale,
                y: line.point.y * scale
            };
            slope = line.slope;
            end = {
                x: start.x + 1,
                y: start.y + slope
            };
        } else {
            throw new Error('Invalid line format');
        }

        const m = slope;
        const b = start.y - m * start.x;

        const intersections = [
            {x: 0, y: b},                          // 왼쪽 경계
            {x: canvasSize, y: m * canvasSize + b},// 오른쪽 경계
            {x: (0 - b) / m, y: 0},                // 위쪽 경계
            {x: (canvasSize - b) / m, y: canvasSize} // 아래쪽 경계
        ];

        const validIntersections = intersections.filter(point => 
            point.x >= 0 && point.x <= canvasSize && 
            point.y >= 0 && point.y <= canvasSize
        );

        if (validIntersections.length >= 2) {
            validIntersections.sort((a, b) => 
                (a.x - b.x) ** 2 + (a.y - b.y) ** 2
            );
            let result = {
                start: adjustPointPosition(validIntersections[0], canvasSize, margin),
                end: adjustPointPosition(validIntersections[1], canvasSize, margin),
            };
            return result;
        }

        function adjustPointPosition(point, canvasSize, margin) {
            return {
                x: Math.max(margin, Math.min(canvasSize - margin, point.x)),
                y: Math.max(margin, Math.min(canvasSize - margin, point.y))
            };
        };

        throw new Error('Line does not intersect canvas properly');
    });
};

function calculateAngleBetweenLines(line1, line2) {
    const slope1 = (line1.end.y - line1.start.y) / (line1.end.x - line1.start.x);
    const slope2 = (line2.end.y - line2.start.y) / (line2.end.x - line2.start.x);

    let angle1 = Math.atan(slope1);
    let angle2 = Math.atan(slope2);

    let angleDiff = Math.abs(angle1 - angle2);

    let acuteAngle = Math.min(angleDiff, Math.PI - angleDiff);

    return (acuteAngle * 180 / Math.PI).toFixed(1);
};

function changeGlobalId(id) {
    if (id >= 0 && id < originalImages.length) {
        global_id = id;
        updateAllCanvases();
    } else {
        console.error("Invalid id");
    }
}

function updateSelectedRow() {
    let table = document.getElementById('dataTable');
    let rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        if (i - 1 === global_id) {
            rows[i].classList.add('selected-row');
        } else {
            rows[i].classList.remove('selected-row');
        }
    }
}

function updateAllCanvases() {
    updateBackground(stage, layer);
    if (stageLarge) {
        updateBackground(stageLarge, layerLarge);
    }

    updateSelectedRow();
}

window.onload = function() {
    updateBackground(stage, layer);
}

backgroundImage.onerror = function() {
    console.error('Error loading background image');
};