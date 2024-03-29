import React, { createContext, useContext, useState, useEffect } from 'react';
import config from '../config';

const DataContext = createContext();

export const useDataContext = () => useContext(DataContext);

export const DataProvider = ({ children }) => {
    const [videosData, setVideosData] = useState({});
    const [channelsData, setChannelsData] = useState({});
    const [statsData, setStatsData] = useState({});

    const fetchVideosData = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}/get/videos`);
            const videosData = await response.json();
            setVideosData(videosData.data);
        } catch (error) {
            console.error('Errore nella richiesta API per i video:', error);
        }
    };

    const fetchChannelsData = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}/get/channels`); 
            const channelsData = await response.json();
            setChannelsData(channelsData.data);
        } catch (error) {
            console.error('Errore nella richiesta API per i canali:', error);
        }
    };

    const fetchStatsData = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}/stats`); 
            const statsData = await response.json();
            setStatsData(statsData.data);
        } catch (error) {
            console.error('Errore nella richiesta API per i canali:', error);
        }
    };

    useEffect(() => {
        fetchVideosData(); 
        fetchChannelsData(); 
        fetchStatsData();
    }, []);

    return (
        <DataContext.Provider value={{ videosData, setVideosData, channelsData, setChannelsData, fetchVideosData, fetchChannelsData, statsData, fetchStatsData }}>
            {children}
        </DataContext.Provider>
    );
};

