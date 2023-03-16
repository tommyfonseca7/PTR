import React from 'react'
import Button from 'react-bootstrap/Button';
import BootStrapModal from 'react-bootstrap/Modal';

import "../App.css";

const Modal = ({isOpen, onClose, onSubmit, onSubmitText='', modalHeading='', modalBody='', onCloseText=''}) => {
  return (
<BootStrapModal show={isOpen} onHide={onClose} centered>
  <BootStrapModal.Header className="modal-header" closeButton>
    <BootStrapModal.Title className="press-start-2p"><h4>{modalHeading}</h4></BootStrapModal.Title>
  </BootStrapModal.Header>
  <BootStrapModal.Body className="press-start-2p"><h6>{modalBody}</h6></BootStrapModal.Body>
  <BootStrapModal.Footer>
    <Button className="custom-button cancel-button" variant="secondary" onClick={onClose}>
      {onCloseText}
    </Button>
    <Button className="custom-button submit-button" variant="primary" onClick={onSubmit}>
      {onSubmitText}
    </Button>
  </BootStrapModal.Footer>
</BootStrapModal>
  );
}

export default Modal
