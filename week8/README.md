# Week 8 — IC Design EDA Report

**Student:** 洪英佩<br>
**Student ID:** 111211147

## 1. Report Objective

This report explains the role of Electronic Design Automation (EDA) in integrated-circuit and FPGA development. It also documents a practical experiment performed with the **veryl2chip web EDA**. The selected project was **Lesson 1: Blinky**, a small digital design that makes LEDs blink on a virtual iCEBreaker FPGA board.

The experiment had four objectives:

1. Run the RTL testbench and confirm the functional behavior.
2. Compare the design after it is translated into different gate libraries.
3. Check whether the design satisfies the requested clock frequency.
4. Load the generated bitstream into a virtual board and observe the output.

## 2. What Is EDA?

Electronic Design Automation is a category of software used to create, simulate, verify, synthesize, and implement electronic systems. Modern chips may contain millions or billions of transistors, so manually drawing and checking every connection is not practical. EDA tools convert a hardware description into lower-level structures and automatically perform many checks during the process.

Unlike an ordinary software program, an HDL description represents hardware that operates concurrently. A design can be logically correct in simulation but still fail on real hardware because of timing, resource, or wiring problems. Therefore, an EDA workflow checks both **what the circuit does** and **whether the circuit can be implemented on the selected device**.

## 3. Typical IC and FPGA Design Flow

```mermaid
flowchart LR
    A[Specification] --> B[RTL Coding]
    B --> C[Simulation]
    C --> D[Synthesis]
    D --> E[Place and Route]
    E --> F[Timing Analysis]
    F --> G[Bitstream or Layout]
    G --> H[Hardware Validation]
```

| Stage | Main purpose | Typical output |
|---|---|---|
| Specification | Define the required behavior, interfaces, and clock | Design requirements |
| RTL coding | Describe registers and data movement using an HDL | Verilog, VHDL, or Veryl source |
| Simulation | Execute a testbench before building hardware | Waveforms and pass/fail results |
| Synthesis | Convert RTL into logic gates or device cells | Gate-level netlist |
| Place and route | Assign cells to physical resources and connect them | Implemented design |
| Timing analysis | Check whether every signal path meets the clock period | Fmax and timing report |
| Bitstream generation | Produce configuration data for an FPGA | FPGA bitstream |
| Hardware validation | Run the final design on a board | Observed device behavior |

Each stage reduces a different type of risk. Simulation detects functional mistakes early, synthesis shows the required hardware resources, and timing analysis determines whether the circuit can operate at the target speed.

## 4. Tool and Experiment Setup

The experiment used the browser-based **veryl2chip IDE**. Veryl is a hardware-description language with a modern syntax, while the web EDA combines the editor, testbench runner, synthesis tools, implementation flow, and a virtual FPGA board.

The project contained these main parts:

| Component | Role in the experiment |
|---|---|
| `Blinky` | The design under test that controls the LEDs |
| `TestBlinky` | The testbench used to verify the design |
| `pins.pcf` | The mapping between logical signals and FPGA pins |
| Virtual iCEBreaker | The simulated FPGA board used for final observation |

The requested design clock was **12 MHz**. This value was used as the timing requirement when the FPGA implementation was generated.

## 5. Experimental Procedure

The following procedure was completed in the web IDE:

1. Opened **Lesson 1: Blinky** and reviewed the available source files and modules.
2. Selected `TestBlinky` and ran the RTL verification.
3. Used **Verify all (RTL + gate level)** to repeat the same test at several implementation levels.
4. Compared the generated cell counts for generic gates, iCE40 cells, and standard cells.
5. Started the virtual iCEBreaker tool.
6. Generated and flashed the FPGA bitstream.
7. Checked the reported logic-cell usage and maximum clock frequency.
8. Observed the LEDs on the virtual board to confirm the final hardware behavior.

Using one testbench at multiple levels is useful because a successful RTL simulation alone does not guarantee that synthesis preserves the intended behavior. Gate-level verification provides an additional comparison after the design has been transformed.

## 6. Verification Results

| Verification target | Result | Implementation information |
|---|---|---|
| RTL | PASS | Original behavioral design |
| Generic gates | PASS | 17 cells |
| iCE40 | PASS | 15 device-specific cells |
| Standard cells | PASS | 17 cells |
| Virtual iCEBreaker | PASS | Bitstream flashed successfully |
| FPGA implementation | PASS | 33 logic cells, Fmax 33.7 MHz |

The RTL test completed successfully, which means the testbench observed the expected logical behavior. The three synthesized representations also passed the same verification. This indicates that the transformations performed during synthesis did not change the externally visible behavior of the Blinky design.

The cell totals are not identical because each target uses a different representation. Generic gates are technology-independent, the iCE40 result maps logic to resources available in that FPGA family, and standard cells represent a cell-library-based implementation. A lower number does not automatically mean a better design because the cells may have different capabilities, sizes, and timing characteristics.

## 7. Timing and Resource Analysis

The target clock was 12 MHz, while the EDA result reported a maximum frequency of 33.7 MHz.

| Timing item | Value |
|---|---:|
| Required frequency | 12.0 MHz |
| Reported Fmax | 33.7 MHz |
| Frequency margin | 21.7 MHz |
| Fmax / required frequency | About 2.81× |

The positive margin is calculated as:

`33.7 MHz - 12.0 MHz = 21.7 MHz`

Because 33.7 MHz is greater than 12 MHz, the implementation satisfies the requested operating frequency. The design could theoretically run faster than the assigned clock, but the clock should still remain within the verified limit. A design that passes functional simulation but reports an Fmax below the required frequency would need optimization, pipelining, or a lower clock target.

The final FPGA result used **33 logic cells**. Blinky is a small project, so its resource usage is low. Even for this simple circuit, the resource report is valuable because the same method scales to larger designs where logic cells, memory blocks, and routing resources may become limited.

## 8. Virtual Board Observation

After the bitstream was flashed, the virtual iCEBreaker displayed a successful programming status. The board simulation ran continuously and the LEDs changed state, producing the expected blinking effect.

This observation completed the path from HDL source code to an implemented hardware result:

- The RTL test checked the intended logic.
- Gate-level tests checked the synthesized representations.
- Timing analysis checked the achievable frequency.
- Bitstream generation configured the FPGA model.
- The virtual LEDs provided a visible system-level result.

The pin-constraint file is important in this final stage. Correct logic can still appear not to work if the clock, reset, or LED signals are assigned to the wrong device pins.

## 9. Why Multiple Verification Levels Matter

An error can be introduced or exposed at different stages. RTL simulation may reveal state-machine or counter mistakes. Synthesis may remove unused logic or map expressions to different cells. Place and route may create long signal paths that fail timing. Board testing may expose incorrect pin assignments or reset behavior.

For this experiment, all verification levels produced matching pass results. The agreement between RTL, generic gates, iCE40 cells, and standard cells provides stronger evidence than one simulation result. It shows that the Blinky design remained consistent as it moved from a high-level description toward a device-specific implementation.

## 10. Advantages and Limitations of the Web EDA

| Advantages | Limitations |
|---|---|
| Runs directly in a browser | The virtual board is not a replacement for all physical tests |
| Combines coding, testing, synthesis, and board simulation | Large projects may require more detailed reports and debugging tools |
| Gives fast feedback for learning | Electrical effects such as power noise are not demonstrated here |
| Allows comparison of several implementation targets | Final results still depend on the selected device and constraints |

The web environment is especially useful for learning because the complete workflow can be observed without installing a local toolchain. For professional IC development, engineers also use detailed waveform inspection, formal verification, power analysis, design-rule checking, and physical signoff tools.

## 11. Conclusion

EDA is the connection between an HDL description and working digital hardware. It automates transformations that would be difficult to perform manually and provides verification at several stages of development.

In the practical exercise, `TestBlinky` passed at RTL and across all three synthesized representations. The virtual iCEBreaker was programmed successfully, the final implementation used 33 logic cells, and the reported Fmax of 33.7 MHz exceeded the 12 MHz requirement by 21.7 MHz. The LEDs also blinked as expected. These results confirm that the design was functionally correct, successfully synthesized, timing-compliant, and operational on the virtual FPGA platform.

## References

- [Week 8 assignment](https://github.com/ccc115a/_co/issues/13)
- [veryl2chip web EDA](https://ccc-eda.github.io/veryl2chip/web/dist/index.html)
- [veryl2chip project](https://github.com/ccc-eda/veryl2chip)
- [Veryl language](https://veryl-lang.org/)
- [Yosys open synthesis suite](https://yosyshq.net/yosys/)
