import React from "react";
import {Avatar, ModalHeader, ModalBody, ModalFooter, Snippet} from "@nextui-org/react";
import { useDataContext } from '../context/Data';
import Video from './Video'

export default function ChannelModal({ channelID, channelName }){     

    const { videosData, channelsData } = useDataContext();

    const handleChannelLinkClick = () => {
        window.open(`https://www.youtube.com/channel/${channelID}`, '_blank');
      };

    return(
        <>
        <ModalHeader className="flex flex-col gap-1"></ModalHeader>
            <ModalBody>
                <div className="flex gap-5 channel-grid">
                    <Avatar className="cursor-pointer" isBordered radius="full" size="lg" src={channelsData[channelID].logo} onClick={handleChannelLinkClick}/>
                    <div className="flex flex-col gap-1 items-start justify-center">
                        <h4 className="text-xl font-semibold leading-none text-default-600 line-clamp-1 cursor-pointer w-[160px]" onClick={handleChannelLinkClick}>{channelName}</h4>
                        <h5 className="text-[0.85rem] tracking-tight text-default-400 font-mono antialiased" >{channelID}</h5>
                    </div>
                </div>
                <div className="video-grid mt-3">
                  {videosData.filter((video) => video.channel === channelID).map((video, index) => (
                      <Video key={index}
                          cardImageSrc={video.thumbnail}
                          avatarSrc={channelsData[video.channel].logo}
                          videoTitle={video.title}
                          videoDuration={video.duration}
                          channelName={channelsData[video.channel].title}
                          channelSubscribers={channelsData[video.channel].subscriberCount}
                          videoPublished={video.published}
                          videoID={video._id}
                          channelID={video.channel}
                          viewed={video.viewed}
                          modal={false}
                      />
                  ))}
                </div>
            </ModalBody>
            <ModalFooter>
            </ModalFooter>
        </>
    )
}