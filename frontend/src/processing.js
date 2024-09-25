import React, { useState } from 'react';
import Header from './components/Header';
import Menu from './components/Menu';
import Footer from './components/Footer';
import AngleSelector from './components/AngleSelector';
import CanvasContainer from './components/CanvasContainer';
import DataTable from './components/DataTable';
import Modal from './components/Modal';

const processing = ({ currentUser, projects, file, angleData }) => {
  const [selectedAngles, setSelectedAngles] = useState(file.selected_angles || []);

  const handleAngleChange = (angle) => {
    setSelectedAngles((prev) =>
      prev.includes(angle) ? prev.filter((a) => a !== angle) : [...prev, angle]
    );
  };

  const selectAllAngles = () => {
    setSelectedAngles(file.selected_angles.length === selectedAngles.length ? [] : file.selected_angles);
  };

  return (
    <div className="is-preload">
      <Header currentUser={currentUser} />
      <Menu projects={projects} />

      <section style={{ padding: '7rem 3rem', maxHeight: '60rem' }}>
        <div className="box alt">
          <div className="processing-container">
            <AngleSelector
              angles={file.selected_angles}
              selectedAngles={selectedAngles}
              handleAngleChange={handleAngleChange}
              selectAllAngles={selectAllAngles}
            />
            <CanvasContainer />
            <DataTable angleData={angleData} selectedAngles={selectedAngles} changeGlobalId={() => console.log('Change global ID')} />
          </div>
        </div>
      </section>

      <Modal />
      <Footer />
    </div>
  );
};

export default processing;
