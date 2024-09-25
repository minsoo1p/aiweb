const breakpoints = {
    xlarge: [1281, 1680],
    large: [981, 1280],
    medium: [737, 980],
    small: [481, 736],
    xsmall: [0, 480],
  };
  
  // Function to check current window size and match the corresponding breakpoint
  export const getBreakpoint = () => {
    const width = window.innerWidth;
    
    if (width >= breakpoints.xlarge[0] && width <= breakpoints.xlarge[1]) return 'xlarge';
    if (width >= breakpoints.large[0] && width <= breakpoints.large[1]) return 'large';
    if (width >= breakpoints.medium[0] && width <= breakpoints.medium[1]) return 'medium';
    if (width >= breakpoints.small[0] && width <= breakpoints.small[1]) return 'small';
    if (width >= breakpoints.xsmall[0] && width <= breakpoints.xsmall[1]) return 'xsmall';
  
    return 'unknown';
  };
  
  export default breakpoints;
  