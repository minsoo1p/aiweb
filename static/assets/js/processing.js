// Define color mapping for each segment
const segmentColors = {
    'cal': {r: 255, g: 0, b: 0},    // Red
    'm1': {r: 0, g: 0, b: 255},           // Blue
    'tib': {r: 0, g: 255, b: 0},        // Green
    'tal': {r: 255, g: 255, b: 0},      // Yellow
    'm5': {r: 255, g: 0, b: 255},         // Magenta
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


// Load the first original image by default
if (originalImages.length > 0) {
    backgroundImage.src = originalImages[0];
} else {
    console.error('No original images available');
}

function updateBackground() {
    var originalImage = originalImages.length > 0 ? originalImages[0] : null;
    var selectedSegmentedImages = [];

    function addSegmentedImage(imageName) {
        var segmentedImage = segmentedImages[Object.keys(segmentedImages)[0]];
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
        addSegmentedImage('cal');
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
        backgroundImage.onload = function() {
            layer.draw();
            drawLines();
        }
    }).catch(error => {
        console.error('Error loading images:', error);
    });
}

// Add event listeners to checkboxes
document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        updateBackground();
        drawLines();
    });
});

// Draw lines
function drawLines() {
    layer.find('Group').forEach(group => group.destroy());

    if (document.getElementById('TibioCalcaneal').checked) {
        drawLinesForAngle('tibiocalcaneal');
    }
    if (document.getElementById('TaloCalcaneal').checked) {
        drawLinesForAngle('talocalcaneal');
    }
    if (document.getElementById('Calcaneal Pitch').checked) {
        drawLinesForAngle('calcanealpitch');
    }
    if (document.getElementById('Meary').checked) {
        drawLinesForAngle('meary');
    }
    if (document.getElementById('Gissane').checked) {
        drawLinesForAngle('gissane');
    }
    if (document.getElementById('Böhler').checked) {
        drawLinesForAngle('bohler');
    }

    updateAngleDisplay();
    layer.batchDraw();
}

function drawLinesForAngle(angleName) {
    var lineObject = lineObjects[Object.keys(lineObjects)[0]];
    if (lineObject && lineObject[angleName]) {
        var lines = lineFitting(lineObject[angleName]);
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
                    updateLineObject(angleName, index, konvaLine, group);
                });

                shape.on('dragmove', function() {
                    updateLine();
                    updateLineObject(angleName, index, konvaLine, group);
                });

                stage.on('mouseout', function() {
                    if (isDragging) {
                        isDragging = false;
                        updateLineObject(angleName, index, konvaLine, group);
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
            displayAngle(angle, lines[0], lines[1]);
        }

        layer.draw();
    }
};

function displayAngle(angle, line1, line2) {
    layer.find('Text').forEach(text => text.destroy());
    layer.find('Arc').forEach(arc => arc.destroy());
    
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

    var angle1 = Math.atan(line1.slope) * 180/Math.PI;
    var angle2 = Math.atan(line2.slope) * 180/Math.PI;

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

    // 텍스트 위치 계산
    const middleAngle = (konvaStartAngle + angle / 2) * Math.PI/180;
    const textOffsetMultiplier = 1.5; // 이 값을 조절하여 텍스트 위치 조정
    const textX = center.x + Math.cos(middleAngle) * 30 * textOffsetMultiplier;
    const textY = center.y + Math.sin(middleAngle) * 30 * textOffsetMultiplier;

    var angleText = new Konva.Text({
        x: textX,
        y: textY,
        text: angle + '°',
        fontSize: 14,
        fill: 'white',
        align: 'center',
    });

    // angleText.offsetX(angleText.width() / 2);
    angleText.offsetY(angleText.height() / 2);

    layer.add(arc);
    layer.add(angleText);
    layer.batchDraw();
};

function updateAngleDisplay() {
    layer.find('Arc').forEach(arc => arc.destroy());
    layer.find('Text').forEach(text => text.destroy());

    const angleMapping = {
        'TibioCalcaneal': 'tibiocalcaneal',
        'TaloCalcaneal': 'talocalcaneal',
        'Calcaneal Pitch': 'calcanealpitch',
        'Meary': 'meary',
        'Gissane': 'gissane',
        'Böhler': 'bohler'
    };

    Object.entries(angleMapping).forEach(([checkboxId, angleName]) => {
        if (document.getElementById(checkboxId).checked) {
            var lineObject = lineObjects[Object.keys(lineObjects)[0]];
            if (lineObject && lineObject[angleName]) {
                var lines = lineFitting(lineObject[angleName]);
                if (lines.length === 2) {
                    var angle = calculateAngleBetweenLines(lines[0], lines[1]);
                    displayAngle(angle, lines[0], lines[1]);
                }
            }
        }
    });

    layer.batchDraw();
}

function updateLineObject(angleName, index, konvaLine, group) {
    var points = konvaLine.points();
    var groupPos = group.position();
    var lineObject = lineObjects[Object.keys(lineObjects)[0]][angleName][index];
    lineObject.start = { x: points[0] + groupPos.x, y: points[1] + groupPos.y };
    lineObject.end = { x: points[2] + groupPos.x, y: points[3] + groupPos.y };
    console.log('Updated line object:', lineObject);

    updateAngleDisplay();
}

function lineFitting(lines, canvasSize = 528, margin = 5) {
    return lines.map(line => {
        let start, end, slope;

        // 첫 번째 형식: start와 end 점이 주어진 경우
        if ('start' in line && 'end' in line) {
            start = line.start;
            end = line.end;
            slope = (end.y - start.y) / (end.x - start.x);
        } 
        // 두 번째 형식: 한 점과 기울기가 주어진 경우
        else if ('point' in line && 'slope' in line) {
            start = line.point;
            slope = line.slope;
            // 임의의 x 값을 사용하여 end 점 계산
            end = {
                x: start.x + 1,
                y: start.y + slope
            };
        } else {
            throw new Error('Invalid line format');
        }

        // y = mx + b 형태의 직선 방정식 계수 계산
        const m = slope;
        const b = start.y - m * start.x;

        // 캔버스 경계와의 교점 계산
        const intersections = [
            {x: 0, y: b},                          // 왼쪽 경계
            {x: canvasSize, y: m * canvasSize + b},// 오른쪽 경계
            {x: (0 - b) / m, y: 0},                // 위쪽 경계
            {x: (canvasSize - b) / m, y: canvasSize} // 아래쪽 경계
        ];

        // 유효한 교점만 필터링
        const validIntersections = intersections.filter(point => 
            point.x >= 0 && point.x <= canvasSize && 
            point.y >= 0 && point.y <= canvasSize
        );

        // 교점이 2개 이상이면 가장 멀리 떨어진 두 점 선택
        if (validIntersections.length >= 2) {
            validIntersections.sort((a, b) => 
                (a.x - b.x) ** 2 + (a.y - b.y) ** 2
            );
            let result = {
                start: adjustPointPosition(validIntersections[0], canvasSize, margin),
                end: adjustPointPosition(validIntersections[validIntersections.length - 1], canvasSize, margin),
                slope: m
            };
            return result;
        }

        throw new Error('Line does not intersect canvas properly');
    });
};

function adjustPointPosition(point, canvasSize, margin) {
    return {
        x: Math.max(margin, Math.min(canvasSize - margin, point.x)),
        y: Math.max(margin, Math.min(canvasSize - margin, point.y))
    };
};

function calculateAngleBetweenLines(line1, line2) {
    // 두 직선의 기울기 사용
    let angle1 = Math.atan(line1.slope);
    let angle2 = Math.atan(line2.slope);

    // 두 각도의 차이 계산 (절대값)
    let angleDiff = Math.abs(angle1 - angle2);

    // 예각 계산 (180도에서 뺌)
    let acuteAngle = Math.min(angleDiff, Math.PI - angleDiff);

    // 라디안에서 도(degree)로 변환
    return (acuteAngle * 180 / Math.PI).toFixed(1);
};


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
    layer.draw();
    drawLines();
};

backgroundImage.onerror = function() {
    console.error('Error loading background image');
};