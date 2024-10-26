import React from 'react';

const Stars = () => {
  const starCount = 50;
  const starsArray = Array.from({ length: starCount });

  return (
    <>
      <style>{`
        body {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background: radial-gradient(ellipse at bottom, #0d1d31 0%, #0c0d13 100%);
          overflow: hidden;
        }

        .stars {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: -100%;
          transform: rotate(-45deg);
        }

        .star {
          position: absolute;
          width: 6em;
          height: 2px;
          background: linear-gradient(45deg, #ffffff, transparent);
          border-radius: 50%;
          filter: drop-shadow(0 0 6px #ffffff);
          transform: translate3d(104em, 0, 0);
          animation: fall 9s linear infinite, tail-fade 9s ease-out infinite;
        }

        .star::before, .star::after {
          position: absolute;
          content: '';
          top: 0;
          left: calc(1em / -2);
          width: 1em;
          height: 100%;
          background: linear-gradient(45deg, transparent, #ffffff, transparent);
          border-radius: inherit;
          animation: blink 2s linear infinite;
        }

        .star::before {
          transform: rotate(45deg);
        }

        .star::after {
          transform: rotate(-45deg);
        }

        @keyframes fall {
          to {
            transform: translate3d(-30em, 0, 0);
          }
        }

        @keyframes tail-fade {
          0%, 50% {
            width: 6em;
            opacity: 1;
          }
          70%, 80% {
            width: 0;
            opacity: 0.4;
          }
          100% {
            width: 0;
            opacity: 0;
          }
        }

        @keyframes blink {
          50% {
            opacity: 0.6;
          }
        }

        ${starsArray.map((_, i) => `
          .star:nth-child(${i + 1}) {
            top: ${Math.random() * 100}vh;
            left: 0;
            animation-duration: ${Math.random() * 6 + 6}s;
            animation-delay: ${Math.random() * 10}s;
          }
        `).join('')}
      `}</style>

      <div className="stars">
        {starsArray.map((_, index) => (
          <div className="star" key={index}></div>
        ))}
      </div>
    </>
  );
};

export default Stars;