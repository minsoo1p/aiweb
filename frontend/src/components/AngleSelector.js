import React from 'react';

const AngleSelector = ({ angles, selectedAngles, handleAngleChange, selectAllAngles }) => {
  return (
    <div
      style={{
        marginTop: '2rem',
        padding: '0.5rem 2rem',
        borderRight: '2px solid #bcbbbb',
        minWidth: '12rem',
        maxHeight: '39rem',
      }}
    >
      <div
        className="box"
        style={{
          fontSize: '14pt',
          borderWidth: '2px',
          marginTop: 0,
          padding: '1rem 0',
          textAlign: 'center',
          backgroundColor: 'rgb(238, 233, 233)',
        }}
      >
        Select Angles
      </div>

      <div className="all-checkbox" style={{ textAlign: 'left', paddingLeft: 'auto', fontSize: '11pt' }}>
        <input type="checkbox" id="All" name="All" onChange={selectAllAngles} />
        <label htmlFor="All" style={{ marginLeft: 0 }}>
          <strong>SELECT ALL</strong>
        </label>
      </div>

      {angles.map((angle, index) => (
        <div key={index} style={{ marginBottom: '0.5rem', fontSize: '11pt' }}>
          <input
            type="checkbox"
            id={angle}
            name={angle}
            checked={selectedAngles.includes(angle)}
            onChange={() => handleAngleChange(angle)}
          />
          <label htmlFor={angle}>{angle}</label>
        </div>
      ))}
    </div>
  );
};


export default AngleSelector;
