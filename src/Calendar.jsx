import { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import huLocale from '@fullcalendar/core/locales/hu';
import './styles/Calendar.css';
import { Popover } from '@mui/material';
import Typography from '@mui/material/Typography';
import momentTimezonePlugin from '@fullcalendar/moment-timezone';

const Calendar = ({ tableData, onCalendarClick, own }) => {
  const [popoverInfo, setPopoverInfo] = useState({
    anchorEl: null,
    event: null,
  });

  const handlePopoverOpen = (event, eventInfo) => {
    setPopoverInfo({ anchorEl: event.currentTarget, event: eventInfo });
  };

  const handlePopoverClose = () => {
    setPopoverInfo({ anchorEl: null, event: null });
  };

  const open = Boolean(popoverInfo.anchorEl);

  const onEventClick = (info) => {
    handlePopoverClose();
    return onCalendarClick(parseInt(info.event.id), own);
  };

  return (
    <>
      <FullCalendar
        plugins={[timeGridPlugin, momentTimezonePlugin]}
        initialView='timeGridWeek'
        weekends={false}
        events={tableData}
        headerToolbar={false}
        allDaySlot={false}
        slotMinTime='08:00:00'
        slotMaxTime='22:00:00'
        locale={huLocale}
        timeZone='Europe/Budapest'
        dayHeaderFormat={{ weekday: 'long' }}
        slotLabelFormat={{
          hour: 'numeric',
          minute: '2-digit',
        }}
        height='auto'
        slotDuration='00:20:00'
        eventClick={onEventClick}
        eventContent={(eventInfo) => {
          return (
            <div
              className={`fc-event-main-frame ${
                eventInfo.event.extendedProps.type === 'gyakorlat'
                  ? 'practice'
                  : 'lecture'
              }`}
              onMouseEnter={(e) => handlePopoverOpen(e, eventInfo)}
              onMouseLeave={handlePopoverClose}
            >
              <div className='fc-event-time'>{eventInfo.timeText}</div>
              <div className='fc-event-title-container'>
                <div className='fc-event-title fc-sticky'>
                  {eventInfo.event.title}
                </div>
              </div>
            </div>
          );
        }}
      />
      {popoverInfo.event && (
        <Popover
          id='mouse-over-popover'
          sx={{ pointerEvents: 'none' }}
          open={open}
          anchorEl={popoverInfo.anchorEl}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          onClose={handlePopoverClose}
          disableRestoreFocus
        >
          <Typography sx={{ p: 1 }}>
            <div>{popoverInfo.event.timeText}</div>
            {popoverInfo.event.event.title.split('\r').map((item, ind) => {
              return <div key={ind}>{item}</div>;
            })}
          </Typography>
        </Popover>
      )}
    </>
  );
};

export default Calendar;
