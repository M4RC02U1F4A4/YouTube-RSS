import React from "react";
import {Card, CardHeader, CardBody, CardFooter, Avatar, Button, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure} from "@nextui-org/react";
import HRNumbers from 'human-readable-numbers';
import { useDataContext } from '../context/Data';
import config from '../config';

export default function Channel({ avatarSrc, channelName, channelDescription, channelSubscribers, channelVideoCount, channelID, channelViewCount, action, stats }){     

    const {isOpen, onOpen, onOpenChange, onClose } = useDisclosure();
    const [backdrop, setBackdrop] = React.useState('opaque')

    const { fetchChannelsData } = useDataContext();

    const handleOpen = (backdrop) => {
        setBackdrop(backdrop)
        onOpen();
    }

    const handleRemoveClick = () => {

        const payload = {
            channel_id: channelID,
        };
      
        fetch(`${config.API_BASE_URL}/remove/channel`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })
          .then(response => response.json())
          .then(data => {
                console.log('Risposta:', data);
                fetchChannelsData();
                onClose();
          })
          .catch(error => {
                console.error('Error:', error);
          });
    };

    const handleAddClick = () => {

      const payload = {
          channel_id: channelID,
      };
    
      fetch(`${config.API_BASE_URL}/add/channel`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
      })
        .then(response => response.json())
        .then(data => {
              console.log('Risposta:', data);
              fetchChannelsData();
              onClose();
        })
        .catch(error => {
              console.error('Error:', error);
        });
    };

    const handleChannelLinkClick = () => {
      window.open(`https://www.youtube.com/channel/${channelID}`, '_blank');
  };

    return(
        <>
        <Card className="w-[313px] h-[188px]">
        <CardHeader className="justify-between">
          <div className="flex gap-5">
            <Avatar className="cursor-pointer" isBordered radius="full" size="md" src={avatarSrc} onClick={handleChannelLinkClick}/>
            <div className="flex flex-col gap-1 items-start justify-center">
              <h4 className="text-small font-semibold leading-none text-default-600 line-clamp-1 cursor-pointer w-[160px]" onClick={handleChannelLinkClick}>{channelName}</h4>
              <h5 className="text-[0.71rem] tracking-tight text-default-400 font-mono antialiased">{channelID}</h5>
            </div>
          </div>
          <div>
          {action === "remove" ? (
              <Button color="danger" radius="full" size="sm" variant="ghost" onPress={() => handleOpen('blur')}>REMOVE</Button>
            ) : action === "add" ? (
              <Button color="success" radius="full" size="sm" variant="ghost" onPress={() => handleAddClick('blur')}>ADD</Button>
            ) : (
              <></>
            )}
          </div>
          
        </CardHeader>
        <CardBody className="px-3 py-0 text-small text-default-400">
          <p className="line-clamp-4">{channelDescription}</p>
        </CardBody>
          <CardFooter className="gap-3">
          {stats === "true" ? (
            <>
              <div className="flex gap-1">
                <p className="font-semibold text-default-400 text-small">{HRNumbers.toHumanString(channelSubscribers)}</p>
                <p className=" text-default-400 text-small">Subs</p>
              </div>
              <div className="flex gap-1">
                <p className="font-semibold text-default-400 text-small">{HRNumbers.toHumanString(channelViewCount)}</p>
                <p className="text-default-400 text-small">Views</p>
              </div>
              <div className="flex gap-1">
                <p className="font-semibold text-default-400 text-small">{HRNumbers.toHumanString(channelVideoCount)}</p>
                <p className="text-default-400 text-small">Videos</p>
              </div>
            </>
            ) : (
              <></>
            )}
          </CardFooter>
        
      </Card>
      <Modal className='dark text-foreground bg-background' isOpen={isOpen} onOpenChange={onOpenChange} backdrop={backdrop} hideCloseButton>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Removing {channelName} channel</ModalHeader>
              <ModalBody>
                <p> 
                  Do you want to continue?
                </p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={() => handleRemoveClick()}>
                  Yes - Remove
                </Button>
                <Button color="primary" onPress={onClose}>
                  No
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
      </>
    )
}