import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTwitter, faFacebookF, faInstagram, faGithub, faLinkedinIn, faEnvelope } from '@fortawesome/free-brands-svg-icons';
import { Modal } from 'react-bootstrap';
import fabric from 'fabric';

function App() {
  const [file, setFile] = useState({ name1: 'Foot', name2: 'AnteroPosterior' });
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showModal, setShowModal] = useState(false);

  const projects = [
    { id: 1, name: 'Project One' },
    { id: 2, name: 'Project Two' },
    { id: 3, name: 'Project Three' }
  ];

  const images = ['image1.png', 'image2.png']; // Placeholder image paths
  const segmentedImages = ['seg_image1.png', 'seg_image2.png'];
  const lineObjects = [
    { lines: [] } // Add line data as needed
  ];

  const handleClose = () => setShowModal(false);
  const handleShow = () => setShowModal(true);

  const nextImage = () => {
    setCurrentImageIndex((currentImageIndex + 1) % images.length);
  };

  const expandImage = () => {
    setShowModal(true);
    loadImage(currentImageIndex, 'modalCanvas', 2);
  };

  const initializeCanvases = () => {
    const mainCanvas = new fabric.Canvas('mainCanvas', {
      width: 512,
      height: 512
    });
    const modalCanvas = new fabric.Canvas('modalCanvas', {
      width: 1024,
      height: 1024
    });
  };

  const loadImage = (index, canvasId, scale = 1) => {
    const canvas = new fabric.Canvas(canvasId);
    canvas.clear();

    const img = new Image();
    img.onload = function () {
      const segImg = new Image();
      segImg.onload = function () {
        const tempCanvas = document.createElement('canvas');
        const tempContext = tempCanvas.getContext('2d');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;

        // Draw the original image
        tempContext.drawImage(img, 0, 0, canvas.width, canvas.height);

        canvas.setBackgroundImage(new fabric.Image(tempCanvas), canvas.renderAll.bind(canvas));

        // Add any line objects here if needed
        if (lineObjects[index] && lineObjects[index].lines) {
          addLineObjects(lineObjects[index].lines, canvas, scale);
        }

        canvas.renderAll();
      };
      segImg.src = segmentedImages[index];
    };
    img.src = images[index];
  };

  useEffect(() => {
    initializeCanvases();
    loadImage(currentImageIndex, 'mainCanvas');
  }, [currentImageIndex]);

  return (
    <div className="App">
      {/* Header */}
      <header id="header">
        <h1><a href="/">AutoAngle</a></h1>
        <a href="#menu">Projects</a>
      </header>

      {/* Menu */}
      <nav id="menu">
        <ul className="links">
          <li><a href="/">Home</a></li>
          <li><a href="/projects">All Projects</a></li>
          {projects.map(project => (
            <li key={project.id}>
              <a href={`/project/${project.id}`}>{project.name}</a>
            </li>
          ))}
        </ul>
        <ul className="actions stacked">
          <li><a href="/logout" className="button primary fit">Logout</a></li>
        </ul>
      </nav>

      {/* Main Section */}
      <section style={{ padding: '7rem 3rem' }}>
        <div className="box alt">
          <div className="row gtr-uniform">
            {/* Left Panel */}
            <div className="col-2" style={{ marginTop: '2rem', padding: '0.5rem 2rem', borderRight: '2px solid #bcbbbb' }}>
              <div className="box" style={{ borderWidth: '2px', padding: '1rem 0', textAlign: 'center', backgroundColor: 'rgb(238, 233, 233)' }}>
                Select Angles
              </div>

              {file.name1 === 'Foot' && file.name2 === 'AnteroPosterior' ? (
                <>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="HVA" name="HVA" />
                    <label htmlFor="HVA">HVA</label>
                  </div>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="DMAA" name="DMAA" />
                    <label htmlFor="DMAA">DMAA</label>
                  </div>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="IMA" name="IMA" />
                    <label htmlFor="IMA">IMA</label>
                  </div>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="TaloCalcaneal" name="TaloCalcaneal" />
                    <label htmlFor="TaloCalcaneal">TaloCalcaneal Angle</label>
                  </div>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="Talonavicular" name="Talonavicular" />
                    <label htmlFor="Talonavicular">TaloNavicular Angle</label>
                  </div>
                  <div className="col-12" style={{ marginBottom: '0.5rem' }}>
                    <input type="checkbox" id="Incongruency" name="Incongruency" />
                    <label htmlFor="Incongruency">Incongruency Angle</label>
                  </div>
                </>
              ) : (
                <>
                  {/* Other angle selection */}
                </>
              )}
            </div>

            {/* Canvas and Buttons */}
            <div className="col-4" style={{ marginTop: '2rem', paddingTop: '0.5rem' }}>
              <div id="imageContainer" style={{ position: 'relative', height: '33rem', width: '33rem' }}>
                <canvas id="mainCanvas" style={{ position: 'absolute', top: 0, left: 0 }}></canvas>
              </div>
              <div style={{ marginTop: '10px' }}>
                <button className="button primary small" onClick={expandImage}>Expand Image</button>
                <button className="button primary small" onClick={nextImage}>Confirm & Save</button>
              </div>
            </div>

            {/* Modal */}
            <Modal show={showModal} onHide={handleClose} size="lg">
              <Modal.Header closeButton>
                <Modal.Title>Expanded Image</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <canvas id="modalCanvas"></canvas>
              </Modal.Body>
              <Modal.Footer>
                <button className="button small" onClick={handleClose}>Close</button>
                <button className="button primary small" onClick={handleClose}>Save</button>
              </Modal.Footer>
            </Modal>

            {/* Table */}
            <div className="col-6" style={{ marginTop: '2rem', paddingTop: '0.5rem', paddingLeft: '0' }}>
              <div style={{ height: '33rem', overflowY: 'auto', padding: 0 }}>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th style={{ width: '7rem' }}>Name</th>
                        <th style={{ width: '6rem' }}>HVA</th>
                        <th style={{ width: '6rem' }}>DMAA</th>
                        <th style={{ width: '6rem' }}>IMA</th>
                        <th style={{ width: '6rem' }}>TaloCalcaneal</th>
                        <th style={{ width: '6rem' }}>TaloNavicular</th>
                        <th style={{ width: '6rem' }}>Incongruency</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Item One</td>
                        <td>12</td>
                        <td>29.99</td>
                        <td>12</td>
                        <td>29.99</td>
                        <td>12</td>
                        <td>29.99</td>
                      </tr>
                      {/* Add more rows as needed */}
                    </tbody>
                  </table>
                </div>
              </div>
              <button className="button fit small">Save and Export Data</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="footer">
        <div className="inner">
          <ul className="icons">
            <li><a href="#" className="icon brands"><FontAwesomeIcon icon={faTwitter} /></a></li>
            <li><a href="#" className="icon brands"><FontAwesomeIcon icon={faFacebookF} /></a></li>
            <li><a href="#" className="icon brands"><FontAwesomeIcon icon={faInstagram} /></a></li>
            <li><a href="#" className="icon brands"><FontAwesomeIcon icon={faGithub} /></a></li>
            <li><a href="#" className="icon brands"><FontAwesomeIcon icon={faLinkedinIn} /></a></li>
            <li><a href="#" className="icon"><FontAwesomeIcon icon={faEnvelope} /></a></li>
          </ul>
          <ul className="contact">
            <li>12345 Somewhere Road</li>
            <li>Nashville, TN 00000</li>
            <li>(000) 000-0000</li>
          </ul>
          <ul className="links">
            <li><a href="#">FAQ</a></li>
            <li><a href="#">Support</a></li>
            <li><a href="#">Terms</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
          <p className="copyright">&copy; Untitled. All rights reserved. Lorem ipsum dolor.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
