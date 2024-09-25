import React from 'react';

const DataTable = ({ angleData, selectedAngles, changeGlobalId }) => {
  return (
    <div style={{ marginTop: '2rem', padding: '0.5rem 1rem', overflowX: 'auto' }}>
      <div
        data-bs-spy="scroll"
        data-bs-root-margin="0px 0px -40%"
        data-bs-smooth-scroll="true"
        className="scrollspy-example bg-body-tertiary rounded-2"
        tabIndex="0"
        style={{ height: '32rem', overflowY: 'auto', padding: '0 0 1rem 0' }}
      >
        <div className="table-wrapper">
          <table id="dataTable">
            <thead>
              <tr>
                <th style={{ width: '7rem', textAlign: 'center' }}>Name</th>
                {selectedAngles.map((angle, index) => (
                  <th key={index} style={{ width: '6rem', textAlign: 'center' }}>
                    {angle}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {angleData.map((row, index) => (
                <tr key={index}>
                  <td style={{ width: '7rem', textAlign: 'center', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                    <a
                      href="#"
                      onClick={() => changeGlobalId(index + 1)}
                      style={{ maxWidth: '12rem', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}
                    >
                      {row.image_name}
                    </a>
                  </td>
                  {selectedAngles.map((angle, idx) => (
                    <td key={idx} style={{ width: '6rem', textAlign: 'center' }} data-angle={angle}>
                      <span>{row[angle]}</span>&#176;
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <li style={{ paddingTop: '6px' }}>
        <a href="#" className="button fit small" style={{ listStyleType: 'none' }} onClick={() => console.log('Data saved and exported')}>
          Save and Export Data
        </a>
      </li>
    </div>
  );
};

export default DataTable;
