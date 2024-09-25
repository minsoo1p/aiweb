import React from 'react';

const CanvasContainer = () => {
  return (
    <div style={{ marginTop: '2rem', paddingTop: '0.5rem', width: '34rem' }}>
      <div
        id="canvasContainer"
        style={{
          width: '32rem',
          height: '32rem',
          marginBottom: '2.2rem',
          position: 'relative',
        }}
      ></div>
      <ul className="actions" style={{ paddingTop: 0, paddingRight: '4rem' }}>
        <li>
          <a
            href="#"
            className="button primary small w-100"
            data-bs-toggle="modal"
            data-bs-target="#staticBackdrop"
            style={{ width: '16rem', fontSize: '11pt' }}
          >
            Expand Image
          </a>
        </li>
        <li>
          <a
            href="#"
            className="button primary small"
            style={{ width: '16rem', fontSize: '11pt' }}
            onClick={() => console.log('Save confirmed')}
          >
            Confirm & Save
          </a>
        </li>
      </ul>
    </div>
  );
};

export default CanvasContainer;
