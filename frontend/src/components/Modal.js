import React from 'react';

const Modal = () => {
  return (
    <div
      className="modal fade"
      id="staticBackdrop"
      data-bs-backdrop="static"
      data-bs-keyboard="false"
      tabIndex="-1"
      aria-labelledby="staticBackdropLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-xl">
        <div className="modal-content">
          <div className="modal-header">
            <h1 className="modal-title fs-5" id="staticBackdropLabel">
              Expanded Image
            </h1>
            <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div className="modal-body d-flex justify-content-center align-items-center">
            <div id="canvasContainerLarge" style={{ width: '64rem', height: '64rem', position: 'relative' }}></div>
          </div>
          <div className="modal-footer">
            <button type="button" className="button small" data-bs-dismiss="modal">
              Close
            </button>
            <button type="button" className="button primary small" data-bs-dismiss="modal" onClick={() => console.log('Expanded image saved')}>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
