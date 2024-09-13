// console.log(originalImages);
// console.log(segmentedImages);
// console.log(lineObjects);

const selectedAngles = file.selected_angles;

// Define mapping as constant
const segmentColors = {
  cal: { r: 255, g: 0, b: 0 }, // Red
  m1: { r: 0, g: 0, b: 255 }, // Blue
  tib: { r: 0, g: 255, b: 0 }, // Green
  tal: { r: 255, g: 255, b: 0 }, // Yellow
  m5: { r: 255, g: 0, b: 255 }, // Magenta
};

var global_id = 1;
var image_number = Object.keys(originalImages).length;
var currentAngles = {};

var lineObject;
var rawLines = {};
var rawLinesExpanded = {};

const angleMapping = {
  // Foot Lateral
  "TibioCalcaneal Angle": ["tib_axis", "cal_tangent"],
  "TaloCalcaneal Angle": ["tal_axis", "cal_tangent"],
  "Calcaneal Pitch": ["cal_tangent", "lowest"],
  "Meary's Angle": ["tal_axis", "m1_axis"],
};

function lineObject_to_rawLines(line_tags, rawLines, lineObject) {
  line_tags.forEach((tag) => {
    switch (tag) {
      case "m1_axis":
        rawLines[tag] = lineObject["m1"]["axis"];
        break;
      case "cal_tangent":
        rawLines[tag] = lineObject["cal"]["tangent"];
        break;
      case "tal_axis":
        rawLines[tag] = lineObject["tal"]["axis"];
        break;
      case "tib_axis":
        rawLines[tag] = lineObject["tib"]["axis"];
        break;
      case "tib_tangent":
        rawLines[tag] = lineObject["tib"]["tangent"];
        break;
      case "lowest":
        rawLines[tag] = [
          lineObject["cal"]["lowest"],
          lineObject["m5"]["lowest"],
        ];
        break;
      default:
        console.error("non available line_tag of selected angle");
    }
  });
}

function lineProcessing(lineObject) {
  let line_tags = new Set();
  selectedAngles.forEach(function (selectedAngle) {
    angleMapping[selectedAngle].forEach((tag) => line_tags.add(tag));
  });
  lineObject_to_rawLines(line_tags, rawLines, lineObject);

  // if ((file.name1 === "Foot") & (file.name2 === "Lateral")) {
  //   rawLines["m1_axis"] = lineObject["m1"]["axis"];
  //   rawLines["cal_tangent"] = lineObject["cal"]["tangent"];
  //   rawLines["tal_axis"] = lineObject["tal"]["axis"];
  //   rawLines["tib_axis"] = lineObject["tib"]["axis"];
  //   rawLines["tib_tangent"] = lineObject["tib"]["tangent"];
  //   rawLines["lowest"] = [lineObject["cal"]["lowest"], lineObject["m5"]["lowest"]];
  // }
}

function updateGlobalId() {
  lineObject = lineObjects[global_id]["content"];
  lineProcessing(lineObject);
}

// Define canvas setting of main canvas
var container = document.getElementById("canvasContainer");
var containerWidth = container.offsetWidth;

var stage = new Konva.Stage({
  container: "canvasContainer",
  width: containerWidth,
  height: containerWidth,
});
var layer = new Konva.Layer();
stage.add(layer);

// Define canvas setting of modal canvas
var stageLarge, layerLarge;

// Canvas 동기화 함수
function syncLines(currentLayer) {
  const line_scaler = currentLayer === layerLarge ? 0.5 : 2;

  if (currentLayer === layerLarge) {
    for (let key in rawLinesExpanded) {
      if (rawLinesExpanded[key] instanceof Array) {
        rawLines[key] = rawLinesExpanded[key].map((line) => {
          return [line[0] * line_scaler, line[1] * line_scaler];
        });
      }
    }
  } else {
    for (let key in rawLines) {
      if (rawLines[key] instanceof Array) {
        rawLinesExpanded[key] = rawLines[key].map((line) => {
          return [line[0] * line_scaler, line[1] * line_scaler];
        });
      }
    }
  }
}

document
  .getElementById("staticBackdrop")
  .addEventListener("shown.bs.modal", function () {
    syncLines(layer);

    var containerLarge = document.getElementById("canvasContainerLarge");
    var containerLargeWidth = containerLarge.offsetWidth;

    if (!stageLarge) {
      stageLarge = new Konva.Stage({
        container: "canvasContainerLarge",
        width: containerLargeWidth,
        height: containerLargeWidth,
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
  syncLines(layerLarge);
  updateBackground(stage, layer);
  var myModalEl = document.getElementById("staticBackdrop");
  var modal = bootstrap.Modal.getInstance(myModalEl);
  modal.hide();
}

var backgroundImage = new Image();

// Load the first original image by default
if (image_number > 0) {
  backgroundImage.src = originalImages[global_id];
} else {
  console.error("No original images available");
}

function updateBackground(targetStage, targetLayer) {
  const originalImage = image_number > 0 ? originalImages[global_id] : null;
  const selectedSegmentedImages = [];
  const segmentSet = new Set();

  function addSegmentedImage(imageName) {
    if (!segmentSet.has(imageName)) {
      const segmentedImage = segmentedImages[global_id];
      if (segmentedImage && segmentedImage[imageName]) {
        selectedSegmentedImages.push({
          src: segmentedImage[imageName],
          name: imageName,
        });
        segmentSet.add(imageName);
      }
    }
  }

  // Collect selected segmented images based on checked angles
  if (document.getElementById("TibioCalcaneal Angle")?.checked) {
    addSegmentedImage("tib");
    addSegmentedImage("cal");
  }
  if (document.getElementById("TaloCalcaneal Angle")?.checked) {
    addSegmentedImage("tal");
    addSegmentedImage("cal");
  }
  if (document.getElementById("Calcaneal Pitch")?.checked) {
    addSegmentedImage("m5");
    addSegmentedImage("cal");
  }
  if (document.getElementById("Meary's Angle")?.checked) {
    addSegmentedImage("m1");
    addSegmentedImage("tal");
  }
  confirmSave;
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
    ...selectedSegmentedImages.map(
      (img) =>
        new Promise((resolve, reject) => {
          const image = new Image();
          image.onload = () => resolve({ image: image, name: img.name });
          image.onerror = reject;
          image.src = img.src;
        })
    ),
  ])
    .then((images) => {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 512;
      const ctx = canvas.getContext("2d");

      // Draw original image at full opacity
      if (images[0]) {
        ctx.globalAlpha = 1;
        ctx.drawImage(images[0], 0, 0, canvas.width, canvas.height);
      }

      // Process and draw segmented images
      for (let i = 1; i < images.length; i++) {
        const segmentedCanvas = document.createElement("canvas");
        segmentedCanvas.width = 512;
        segmentedCanvas.height = 512;
        const segmentedCtx = segmentedCanvas.getContext("2d");

        segmentedCtx.drawImage(
          images[i].image,
          0,
          0,
          segmentedCanvas.width,
          segmentedCanvas.height
        );
        const imageData = segmentedCtx.getImageData(
          0,
          0,
          segmentedCanvas.width,
          segmentedCanvas.height
        );
        const data = imageData.data;

        const color = segmentColors[images[i].name] || {
          r: 128,
          g: 128,
          b: 128,
        }; // Default to gray if color not found

        for (let j = 0; j < data.length; j += 4) {
          if (data[j] < 30 && data[j + 1] < 30 && data[j + 2] < 30) {
            // Change black background to white
            // data[j] = 255;
            // data[j+1] = 255;
            // data[j+2] = 255;
            data[j + 3] = 0; // Make it transparent
          } else {
            // Apply specific color to the bone mask
            data[j] = color.r;
            data[j + 1] = color.g;
            data[j + 2] = color.b;
            data[j + 3] = 128; // Semi-transparent
          }
        }

        segmentedCtx.putImageData(imageData, 0, 0);

        // Draw the processed segmented image onto the main canvas
        ctx.globalAlpha = 0.5;
        ctx.drawImage(segmentedCanvas, 0, 0, canvas.width, canvas.height);
      }

      backgroundImage.src = canvas.toDataURL();
      backgroundImage.onload = function () {
        updateCanvasWithBackground(targetStage, targetLayer);
      };
    })
    .catch((error) => {
      console.error("Error loading images:", error);
    });
}

function updateCanvasWithBackground(targetStage, targetLayer) {
  var target_images = targetLayer.find("Image");
  target_images.forEach((image) => image.destroy());

  var image = new Konva.Image({
    x: 0,
    y: 0,
    image: backgroundImage,
    width: targetStage.width(),
    height: targetStage.height(),
  });
  targetLayer.add(image);
  drawLines(targetStage, targetLayer);
  targetLayer.draw();
}

// Add event listeners to checkboxes
document.addEventListener("DOMContentLoaded", function () {
  const allCheckbox = document.getElementById("All");
  const angleCheckboxes = document.querySelectorAll(
    'input[type="checkbox"]:not(#All)'
  );

  allCheckbox.addEventListener("change", function () {
    angleCheckboxes.forEach((checkbox) => {
      checkbox.checked = this.checked;
    });
    updateBackground(stage, layer);
  });

  angleCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      allCheckbox.checked = Array.from(angleCheckboxes).every(
        (cb) => cb.checked
      );
      updateBackground(stage, layer);
    });
  });
});

function updateTableWithAngles(id) {
  let table = document.getElementById("dataTable");
  let currentRow = table.rows[id];

  for (let [key, value] of Object.entries(currentAngles)) {
    let cell = currentRow.querySelector(`td[data-angle="${key}"]`);
    let cellValue = cell.getElementsByTagName("span")[0];
    if (cellValue) {
      cellValue.textContent = value.toFixed(1);
    }
  }
}

function confirmSave() {
  updateTableWithAngles(global_id);

  if (global_id < image_number) {
    global_id++;
    updateAllCanvases();
  } else {
    alert("You have reached the last image.");
  }
}

function saveAndExportData() {
  let table = document.getElementById("dataTable");
  let data = [];

  for (let i = 1; i < table.rows.length; i++) {
    let row = table.rows[i];
    let rowData = { image_name: row.cells[0].textContent };

    selectedAngles.forEach((selectedAngle, index) => {
      let selectedAngle_csvStyle = selectedAngle
        .replace(/'/g, "")
        .replace(/ /g, "_");
      rowData[selectedAngle_csvStyle] =
        row.cells[index + 1].getElementsByTagName("span")[0].textContent;
    });
    data.push(rowData);
  }

  fetch(`/save_and_download/${file.id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.ok) {
        return response.blob();
      }
      throw new Error("Network response was not ok.");
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = "angles.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Error saving and exporting data.");
    });
}

// Draw lines
function drawLines(stage, layer) {
  layer.find("Group").forEach((group) => group.destroy());

  selectedAngles.forEach((angle) => {
    if (document.getElementById(angle).checked) {
      drawLinesForAngle(angle, stage, layer);
    }
  });

  updateTableWithAngles(global_id);
}

function drawLinesForAngle(angle, stage, layer) {
  const mapped_lines = angleMapping[angle];
  if (layer === layerLarge) {
    var targetLines = [
      rawLinesExpanded[mapped_lines[0]],
      rawLinesExpanded[mapped_lines[1]],
    ];
  } else {
    var targetLines = [rawLines[mapped_lines[0]], rawLines[mapped_lines[1]]];
  }

  if (lineObject && targetLines) {
    var lines = lineFitting(targetLines, stage.width());

    lines.forEach((line, index) => {
      var konvaLine = new Konva.Line({
        points: [line.start.x, line.start.y, line.end.x, line.end.y],
        stroke: "yellow",
        strokeWidth: 2,
      });

      var startAnchor = new Konva.Circle({
        x: line.start.x,
        y: line.start.y,
        radius: 3,
        fill: "white",
        stroke: "green",
        strokeWidth: 2,
        draggable: true,
      });

      var endAnchor = new Konva.Circle({
        x: line.end.x,
        y: line.end.y,
        radius: 3,
        fill: "white",
        stroke: "green",
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

      function updateLine() {
        var points = [
          startAnchor.x(),
          startAnchor.y(),
          endAnchor.x(),
          endAnchor.y(),
        ];
        konvaLine.points(points);
      }

      function addDragBehaviorLazy(shape) {
        shape.on("dragmove", function () {
          updateLine();
          // layer.batchDraw();
          updateLineObject(lines, index, konvaLine, group, layer, angle);
        });

        shape.on("dragend", function () {
          updateLineObject(lines, index, konvaLine, group, layer, angle);
          updateBackground(stage, layer);
        });
      }

      addDragBehaviorLazy(group);
      addDragBehaviorLazy(startAnchor);
      addDragBehaviorLazy(endAnchor);

      startAnchor.on("dragmove", function () {
        updateLine();
        layer.batchDraw();
      });

      endAnchor.on("dragmove", function () {
        updateLine();
        layer.batchDraw();
      });

      group.on("dragmove", function () {
        // updateLine();/
        layer.batchDraw();
      });

      group.on("mouseenter", function () {
        stage.container().style.cursor = "move";
      });

      group.on("mouseleave", function () {
        stage.container().style.cursor = "default";
      });

      startAnchor.on("mouseenter", function () {
        stage.container().style.cursor = "pointer";
      });

      endAnchor.on("mouseenter", function () {
        stage.container().style.cursor = "pointer";
      });
    });

    if (lines.length === 2) {
      var angleValue = calculateAngleBetweenLines(lines[0], lines[1]);
      displayAngle(angleValue, lines[0], lines[1], layer, angle);
    }
  }
}

function displayAngle(angleValue, line1, line2, layer, angle) {
  // layer.find('Text').forEach(text => text.destroy());
  // layer.find('Arc').forEach(arc => arc.destroy());

  currentAngles[angle] = parseFloat(angleValue);

  const x1 = line1.start.x,
    y1 = line1.start.y;
  const x2 = line1.end.x,
    y2 = line1.end.y;
  const x3 = line2.start.x,
    y3 = line2.start.y;
  const x4 = line2.end.x,
    y4 = line2.end.y;

  const denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);

  const t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator;
  const u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator;

  if (denominator === 0) {
    var center = null;
  } else {
    var center = {
      x: x1 + t * (x2 - x1),
      y: y1 + t * (y2 - y1),
    };
  }
  const slope1 = (line1.end.y - line1.start.y) / (line1.end.x - line1.start.x);
  const slope2 = (line2.end.y - line2.start.y) / (line2.end.x - line2.start.x);

  var angle1 = (Math.atan(slope1) * 180) / Math.PI;
  var angle2 = (Math.atan(slope2) * 180) / Math.PI;

  var startAngle = Math.min(angle1, angle2);
  var endAngle = Math.max(angle1, angle2);

  let konvaStartAngle;

  if (endAngle - startAngle > 90) {
    konvaStartAngle = endAngle;
  } else {
    konvaStartAngle = startAngle;
  }

  var arc = new Konva.Arc({
    x: center.x,
    y: center.y,
    innerRadius: 0,
    outerRadius: 30,
    angle: angleValue,
    rotation: konvaStartAngle,
    clockwise: false,
    fill: "white",
    opacity: 0.7,
  });

  const middleAngle = ((konvaStartAngle + angleValue / 2) * Math.PI) / 180;
  const textOffsetMultiplier = 1.8;
  const textX = center.x + Math.cos(middleAngle) * 30 * textOffsetMultiplier;
  const textY = center.y + Math.sin(middleAngle) * 30 * textOffsetMultiplier;

  var angleText = new Konva.Text({
    x: textX,
    y: textY,
    text: angleValue + "°",
    fontSize: 16,
    fill: "white",
    align: "center",
  });

  angleText.offsetX(angleText.width() / 2);
  angleText.offsetY(angleText.height() / 2);

  layer.add(arc);
  layer.add(angleText);
}

function updateLineObject(lines, index, konvaLine, group, layer, angle) {
  let mapped_lines = angleMapping[angle];
  var points = konvaLine.points();
  var groupPos = group.position();

  lines[index].start = { x: points[0] + groupPos.x, y: points[1] + groupPos.y };
  lines[index].end = { x: points[2] + groupPos.x, y: points[3] + groupPos.y };

  if (layer === layerLarge) {
    rawLinesExpanded[mapped_lines[index]] = [
      [lines[index].start.x, lines[index].start.y],
      [lines[index].end.x, lines[index].end.y],
    ];
  } else {
    rawLines[mapped_lines[index]] = [
      [lines[index].start.x, lines[index].start.y],
      [lines[index].end.x, lines[index].end.y],
    ];
  }

  layer.find("Arc").forEach((arc) => arc.destroy());
  layer.find("Text").forEach((text) => text.destroy());

  if (lines.length === 2) {
    var angleValue = calculateAngleBetweenLines(lines[0], lines[1]);
    displayAngle(angleValue, lines[0], lines[1], layer, angle);
  }
}

function lineFitting(lines, canvasSize = 512, margin = 15) {
  // const scale = canvasSize / 512;

  // return lines.map((line) => {
  //   let start, end, slope;

  //   if (line.length === 2) {
  //     start = {
  //       x: line[0][0] * scale,
  //       y: line[0][1] * scale,
  //     };
  //     end = {
  //       x: line[1][0] * scale,
  //       y: line[1][1] * scale,
  //     };
  //     slope = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0]);
  //   } else {
  //     throw new Error("The number of points of lines is not 2");
  //   }

  return lines.map((line) => {
    let start, end, slope;

    if (line.length === 2) {
      start = {
        x: line[0][0],
        y: line[0][1],
      };
      end = {
        x: line[1][0],
        y: line[1][1],
      };
      slope = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0]);
    } else {
      throw new Error("The number of points of lines is not 2");
    }

    const m = slope;
    const b = start.y - m * start.x;

    const intersections = [
      { x: 0, y: b }, // 왼쪽 경계
      { x: canvasSize, y: m * canvasSize + b }, // 오른쪽 경계
      { x: (0 - b) / m, y: 0 }, // 위쪽 경계
      { x: (canvasSize - b) / m, y: canvasSize }, // 아래쪽 경계
    ];

    const validIntersections = intersections.filter(
      (point) =>
        point.x >= 0 &&
        point.x <= canvasSize &&
        point.y >= 0 &&
        point.y <= canvasSize
    );

    if (validIntersections.length >= 2) {
      validIntersections.sort((a, b) => (a.x - b.x) ** 2 + (a.y - b.y) ** 2);
      let result = {
        start: adjustPointPosition(validIntersections[0], canvasSize, margin),
        end: adjustPointPosition(validIntersections[1], canvasSize, margin),
      };
      return result;
    }

    function adjustPointPosition(point, canvasSize, margin) {
      var adjusted_x, adjusted_y;
      const del_x = Math.sqrt(margin ** 2 / (m ** 2 + 1));
      const del_y = Math.sqrt(margin ** 2 / (m ** 2 + 1)) * Math.abs(m);

      if (point.x === 0) {
        adjusted_x = point.x + del_x;
        adjusted_y = point.y + del_x * m;
      } else if (point.x === canvasSize) {
        adjusted_x = point.x - del_x;
        adjusted_y = point.y - del_x * m;
      } else if (point.y === 0) {
        adjusted_x = point.x + del_y / m;
        adjusted_y = point.y + del_y;
      } else {
        adjusted_x = point.x - del_y / m;
        adjusted_y = point.y - del_y;
      }

      return {
        x: adjusted_x,
        y: adjusted_y,
      };
    }

    throw new Error("Line does not intersect canvas properly");
  });
}

function calculateAngleBetweenLines(line1, line2) {
  const slope1 = (line1.end.y - line1.start.y) / (line1.end.x - line1.start.x);
  const slope2 = (line2.end.y - line2.start.y) / (line2.end.x - line2.start.x);

  let angle1 = Math.atan(slope1);
  let angle2 = Math.atan(slope2);

  let angleDiff = Math.abs(angle1 - angle2);

  let acuteAngle = Math.min(angleDiff, Math.PI - angleDiff);

  return ((acuteAngle * 180) / Math.PI).toFixed(1);
}

function changeGlobalId(id) {
  if (id > 0 && id <= image_number) {
    global_id = id;
    updateAllCanvases();
  } else {
    console.error("Invalid id");
  }
}

function updateSelectedRow() {
  let table = document.getElementById("dataTable");
  let rows = table.getElementsByTagName("tr");

  for (let i = 1; i < rows.length; i++) {
    if (i === global_id) {
      rows[i].classList.add("selected-row");
    } else {
      rows[i].classList.remove("selected-row");
    }
  }
}

function updateAllCanvases() {
  updateGlobalId();

  updateBackground(stage, layer);
  if (stageLarge) {
    updateBackground(stageLarge, layerLarge);
  }

  updateSelectedRow();
}

function calculateAngleOnly(id) {
  global_id = id;
  updateGlobalId();

  selectedAngles.forEach((selectedAngle) => {
    const mapped_lines = angleMapping[selectedAngle];
    var targetLines = [rawLines[mapped_lines[0]], rawLines[mapped_lines[1]]];
    if (rawLines && targetLines) {
      var lines = lineFitting(targetLines);
    }
    var angleValue = calculateAngleBetweenLines(lines[0], lines[1]);
    currentAngles[selectedAngle] = parseFloat(angleValue);
  });
  updateTableWithAngles(id);
}

window.onload = function () {
  document.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    checkbox.checked = true;
  });

  for (let id = 1; id <= image_number; id++) {
    calculateAngleOnly(id);
  }
  global_id = 1;
  currentAngles = {};

  updateGlobalId();
  updateBackground(stage, layer);
  updateSelectedRow();
};

backgroundImage.onerror = function () {
  console.error("Error loading background image");
};
