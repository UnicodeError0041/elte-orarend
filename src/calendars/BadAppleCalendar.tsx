import '../styles/Calendar.css';

import LinkIcon from '@mui/icons-material/Link';
import { Badge, Button } from '@mui/material';
import { generateUniqueId, type Lesson } from '../utils/data';
import LessonCalendar from './LessonCalendar';
import { useState, useEffect, useRef, useCallback } from 'react';

type LessonBlock = {
    lesson: Lesson;
    order: number;
    start_time: number;
    end_time: number;
};

type LessonVideo = {
    blocks: LessonBlock[];
    fps: number;
};

type BadAppleCalendarProps = {
    onUrlExport: () => void; // URL export kezelő
    onImageDownload: (ref: React.MutableRefObject<HTMLElement>) => Promise<void>; // Kép mentés kezelő
};

type States = {
    lessons: Lesson[],
    data: LessonVideo | null,
    frameCount: number
}

const BadAppleCalendar: React.FC<BadAppleCalendarProps> = ({
    onUrlExport,
    onImageDownload,
}: BadAppleCalendarProps) => {
    // const [lessons, setLessons] = useState<Lesson[]>([]);
    // const [data, setData] = useState<LessonVideo | null>(null);
    // const [frameCount, setFrameCount] = useState(0);

    const [states, setStates] = useState<States>({
        lessons: [],
        data: null,
        frameCount: 0
    })
    // const [frames, setFrames] = useState<Lesson[][]>([]);
    const playingRef = useRef(false);


    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Fetch the video data once
    useEffect(() => {
        fetch("http://localhost:8000/bad_apple.php")
            .then((resp) => resp.json() as Promise<LessonVideo>)
            .then((data_) => {
                data_.blocks.sort((a, b) => a.order - b.order);
                for(let block of data_.blocks){
                    block.lesson.id = generateUniqueId(block.lesson);
                }
                
                // let frameCount = 0;
                // let frames_ = [];

                // let frame = data_.blocks
                // .filter(
                //     (block) =>
                //         block.start_time <= frameCount &&
                //         block.end_time >= frameCount
                // )
                // .map(
                //     (block) => block.lesson,
                // );

                // while(frame.length !== 0){
                //     frames_.push(frame);

                //     frameCount++;
                //     frame = data_.blocks
                //         .filter(
                //             (block) =>
                //                 block.start_time <= frameCount &&
                //                 block.end_time >= frameCount
                //         )
                //         .map(
                //             (block) => block.lesson,
                //         );
                // }

                // setFrames(frames_);
            
                console.log(data_.blocks.length);
                setStates({...states, data:data_});
            });
    }, []);

    // Update lessons whenever frameCount changes
    useEffect(() => {
        if (states.data) {
            const visibleLessons = states.data.blocks
                .filter(
                    (block) =>
                        block.start_time <= states.frameCount &&
                        block.end_time >= states.frameCount
                )
                .map(
                    (block) => block.lesson,
                );
            // const visibleLessons = frames[frameCount];
            setStates({...states, lessons: visibleLessons});
        }
    }, [states]);

    // Play video loop
    const playWithThrottling = useCallback(() => {
        if (!states.data || playingRef.current) return;
        playingRef.current = true;
    
        let lastRenderTime = performance.now();

        if (audioRef.current) {
            audioRef.current.currentTime = 0; // Reset to the start
            audioRef.current.play();
        }
    
        const play = () => {
            const now = performance.now();
            if (now - lastRenderTime >= 20000 / (states.data as LessonVideo).fps) {
                setStates((prev) => {
                    prev.frameCount += 1;
                    // if (nextFrame >= data.blocks[data.blocks.length - 1].end_time) {
                    //     playingRef.current = false;
                    //     return prev;
                    // }
                    return prev;
                });
                lastRenderTime = now;
            }
    
            if (playingRef.current) {
                requestAnimationFrame(play);
            }
        };
        play();
    }, [states]);

    const stopPlayback = () => {
        playingRef.current = false;
        if (audioRef.current !== null){
            audioRef.current.pause();
        }
    };

    return (
        <LessonCalendar
            lessons={states.lessons}
            onImageDownload={onImageDownload}
            calendarClassNames='bad-apple-calendar'
            onEventClick={(_) => playWithThrottling()}
            // showPopover
            eventContent={(eventInfo) => {
                return (
                    <div
                        className={`view-only ${
                            eventInfo.event.extendedProps.type === 'gyakorlat'
                                ? 'practice'
                                : 'lecture'
                        }`}
                    >
                        <div className="fc-event-time">
                            <b>{eventInfo.timeText}</b>
                        </div>
                        <div className="fc-event-title-container">
                            <div className="fc-event-title fc-sticky">
                                {eventInfo.event.title}
                            </div>
                        </div>
                    </div>
                );
            }}
        >
            <Badge badgeContent="ÚJ" color="secondary">
                <Button
                    variant="outlined"
                    startIcon={<LinkIcon />}
                    onClick={onUrlExport}
                    fullWidth
                >
                    Mentés hivatkozásként
                </Button>
            </Badge>

            {/* <Button
                variant="outlined"
                onClick={() => setStates({...states, frameCount: states.frameCount+1})}
            >
                Next frame current: {states.frameCount}
            </Button>
            <Button variant="outlined" onClick={playWithThrottling}>
                Play
            </Button>
            <Button variant="outlined" onClick={stopPlayback}>
                Stop
            </Button> */}

            <audio ref={audioRef} src="audio.mp3" muted/>
        </LessonCalendar>
    );
};

export default BadAppleCalendar;
