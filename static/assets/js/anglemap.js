// selected anlge에서 필요한 line명으로 mapping하는 dictionary

export const angleMapping = {
    // Foot Lateral
    'TibioCalcaneal Angle': ['tib_axis', 'cal_tangent'],
    'TaloCalcaneal Angle': ['tal_axis', 'cal_tangent'],
    'Calcaneal Pitch': ['cal_tangent', 'lowest'],
    "Meary's Angle": ['tal_axis', 'm1_axis'],

    // Foot AP

}

export default function lineObject_to_rawLines(selectedAngle, rawLines, lineObject) {
    let line_tags = angleMapping[selectedAngle];
    line_tags.forEach((tag) =>{
        if (!(tag in rawLines)) {
            switch (tag) {
                case 'm1_axis':
                    rawLines[tag] = lineObject["m1"]["axis"];
                    break;
                case 'cal_tangent':
                    rawLines[tag] = lineObject["cal"]["tangent"];
                    break;
                case 'tal_axis':
                    rawLines[tag] = lineObject["tal"]["axis"];
                    break;
                case 'tib_axis':
                    rawLines[tag] = lineObject["tib"]["axis"];
                    break;
                case 'tib_tangent':
                    rawLines[tag] = lineObject["tib"]["tangent"];
                    break;
                case 'lowest':
                    rawLines[tag] = [lineObject["cal"]["lowest"], lineObject["m5"]["lowest"]];
                    break;
                default:
                    console.error('non available line_tag of selected angle');
            }
        }
    })
    console.log(rawLines);
}