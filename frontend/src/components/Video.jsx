import React from "react";
import {Card, CardHeader, CardBody, Image} from "@nextui-org/react";
import {Avatar, Modal, ModalContent, useDisclosure} from "@nextui-org/react";
import moment from 'moment';
import { useDataContext } from '../context/Data';
import config from '../config';
import ChannelModal from "./ChannelModal";

export default function Video({ cardImageSrc, avatarSrc, videoTitle, channelName, videoDuration, videoPublished, videoID, channelID, viewed, modal, home }){

    const formatDuration = (durationInSeconds) => {
        return moment.utc(moment.duration(durationInSeconds, 'seconds').asMilliseconds()).format('HH:mm:ss').replace(/^00:/, '');;
    };

    const getTimeAgoString = (dateString) => {
      const currentDate = moment();
      const inputDate = moment(dateString);
  
      const diffInMinutes = currentDate.diff(inputDate, 'minutes');
      const diffInHours = currentDate.diff(inputDate, 'hours');
      const diffInDays = currentDate.diff(inputDate, 'days');
      const diffInMonths = currentDate.diff(inputDate, 'months');
      const diffInYears = currentDate.diff(inputDate, 'years');
  
      if (diffInMinutes < 60) {
          return `${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`;
      } else if (diffInHours < 24) {
          return `${diffInHours} ${diffInHours === 1 ? 'hour' : 'hours'} ago`;
      } else if (diffInDays < 30) {
          return `${diffInDays} ${diffInDays === 1 ? 'day' : 'days'} ago`;
      } else if (diffInMonths < 12) {
          return `${diffInMonths} ${diffInMonths === 1 ? 'month' : 'months'} ago`;
      } else {
          return `${diffInYears} ${diffInYears === 1 ? 'year' : 'years'} ago`;
      }
    };
  

    const { fetchVideosData, fetchStatsData } = useDataContext();

    const handleVideoLinkClick = (event) => {
        event.preventDefault();
        window.open(`https://www.youtube.com/watch?v=${videoID}`, '_blank');
        fetch(`${config.API_BASE_URL}/watch/video/${videoID}`, {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                fetchVideosData();
                fetchStatsData();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };

    const handleViewLinkClick = (event) => {
        event.preventDefault();
      
        fetch(`${config.API_BASE_URL}/watch/video/${videoID}`, {
          method: 'GET',
        })
          .then(response => response.json())
          .then(data => {
            console.log(data);
            fetchVideosData();
            fetchStatsData();
          })
          .catch(error => {
            console.error('Error:', error);
          });
    };

    const handleToViewLinkClick = (event) => {
        event.preventDefault();
      
        fetch(`${config.API_BASE_URL}/tbwatch/video/${videoID}`, {
          method: 'GET',
        })
          .then(response => response.json())
          .then(data => {
            console.log(data);
            fetchVideosData();
            fetchStatsData();
          })
          .catch(error => {
            console.error('Error:', error);
          });
    };

    const { isOpen: isChannelModalOpen, onOpen: onChannelModalOpen, onClose: onChannelModalClose } = useDisclosure();

    const handleChannelLinkClickForModal = () => {
      onChannelModalOpen();
    };

    const handleVideoLinkClickNoView = () => {
      window.open(`https://www.youtube.com/watch?v=${videoID}`, '_blank');
    };

    return(
      <>
      {modal ? (
        <Card className="w-[313px] h-[282px] border-none bg-transparent" shadow="none">
            <CardHeader className="pb-0 pt-2 px-4 flex-col items-start relative">
                <div className="relative">
                    <Image className="object-cover rounded-xl cursor-pointer w-[281px] h-[158px]" src={cardImageSrc} onClick={handleVideoLinkClick} />
                    <div className="absolute bottom-0 right-0 p-2 z-10">
                        <p className="text-xs bg-black bg-opacity-85 text-white font-bold px-1 rounded">{formatDuration(videoDuration)}</p>
                    </div>
                    <div className="absolute bottom-0 left-0 p-2 z-10">
                        <p className="text-xs bg-black bg-opacity-85 text-white font-bold px-1 rounded">{getTimeAgoString(videoPublished)}</p>
                    </div>
                </div>
            </CardHeader>
            <CardBody className="overflow-visible py-2 px-4 w-[281px] mt-1">
                <div className="flex gap-5">
                      <div>
                          <Avatar src={avatarSrc} onClick={handleChannelLinkClickForModal} size="md" className="w-[40px] cursor-pointer" />
                      </div>
                      <div className="flex flex-col gap-1 items-start justify-center">
                        {viewed === 1 ? (
                          <a className="uppercase text-sm font-bold antialiased text-green-600 hover:text-green-500 cursor-pointer" onClick={handleToViewLinkClick}>Mark as to be watched</a>
                        ) : (
                          <a className="uppercase text-sm font-bold antialiased text-red-600 hover:text-red-500 cursor-pointer" onClick={handleViewLinkClick}>Mark as watched</a>
                        )}
                        <a className="text-base font-semibold antialiased text-sky-500 line-clamp-2 cursor-pointer" onClick={handleVideoLinkClick} >{videoTitle}</a>
                        <a className="text-xs font-medium antialiased text-white-600 cursor-pointer line-clamp-1" onClick={handleChannelLinkClickForModal}>{channelName}</a>
                      </div>
                </div>
            </CardBody>
            <Modal isOpen={isChannelModalOpen} scrollBehavior='inside' onOpenChange={onChannelModalClose} size="4xl" className="dark text-foreground bg-background" backdrop="blur" hideCloseButton>
              <ModalContent>
                {(onChannelModalClose) => (
                  <>
                    <ChannelModal channelID={channelID} channelName={channelName}/>
                  </>
                )}
              </ModalContent>
            </Modal>
        </Card>
        ) : (
          <Card className="w-[313px] h-[222px] border-none bg-transparent" shadow="none">
            <CardHeader className="pb-0 pt-2 px-4 flex-col items-start relative">
                <div className="relative">
                    <Image className="object-cover rounded-xl cursor-pointer w-[281px] h-[158px]" src={cardImageSrc} onClick={handleVideoLinkClickNoView} />
                    <div className="absolute bottom-0 right-0 p-2 z-10">
                        <p className="text-xs bg-black bg-opacity-85 text-white font-bold px-1 rounded">{formatDuration(videoDuration)}</p>
                    </div>
                    <div className="absolute bottom-0 left-0 p-2 z-10">
                        <p className="text-xs bg-black bg-opacity-85 text-white font-bold px-1 rounded">{getTimeAgoString(videoPublished)}</p>
                    </div>
                    {viewed === 1 ? (
                      <div className="absolute top-0 right-0 p-2 z-10">
                        <p className="text-xs bg-black bg-opacity-85 text-white font-bold px-1 rounded">Watched</p>
                      </div>
                    ) : (
                      <></>
                    )}
                </div>
            </CardHeader>
            <CardBody className="overflow-visible py-2 px-4 w-[313px] mt-1">
                  <div className="flex gap-5">
                        <>
                          <div className="flex flex-col gap-1 items-start justify-center">
                            <a className="text-base font-semibold antialiased text-sky-500 line-clamp-2 cursor-pointer" onClick={handleVideoLinkClickNoView} >{videoTitle}</a>
                          </div>
                        </>
                      
                  </div>
              </CardBody>
            <Modal isOpen={isChannelModalOpen} scrollBehavior='inside' onOpenChange={onChannelModalClose} size="4xl" className="dark text-foreground bg-background" backdrop="blur" hideCloseButton>
              <ModalContent>
                {(onChannelModalClose) => (
                  <>
                    <ChannelModal channelID={channelID} channelName={channelName}/>
                  </>
                )}
              </ModalContent>
            </Modal>
        </Card>
        )}
        </>
    )
}


